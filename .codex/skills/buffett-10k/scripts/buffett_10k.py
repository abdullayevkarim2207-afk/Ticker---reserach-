#!/usr/bin/env python3
"""Keyless SEC EDGAR 10-K facts and Buffett checks for FIN 43900 Lab 18."""

from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
FLOW_MIN_DAYS = 300
FLOW_MAX_DAYS = 430

METRIC_TAGS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
    ],
    "net_income": ["NetIncomeLoss"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capital_spending": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ],
    "equity": ["StockholdersEquity"],
}

METRIC_LABELS = {
    "revenue": "Revenue",
    "net_income": "Net income",
    "operating_cash_flow": "Operating cash flow",
    "capital_spending": "Capital spending",
    "equity": "Equity",
    "roe": "ROE",
    "owner_earnings": "Owner earnings",
}

CHECK_LABELS = {
    "roe_15_every_year": "ROE of 15% or more every year",
    "owner_earnings_positive_every_year": "Owner earnings positive every year",
    "owner_earnings_grew": "Owner earnings grew, first year to last",
}

NUMBER_RE = re.compile(r"(?<![\d,])(?:\$\s*)?-?\d[\d,]*(?:\.\d+)?%?")


class EdgarError(RuntimeError):
    """A readable failure while retrieving or interpreting SEC data."""


def validate_user_agent(user_agent: str | None) -> str:
    """Require the SEC-requested name-and-email identity without persisting it."""
    value = (user_agent or "").strip()
    if "@" not in value or len(value.split()) < 2:
        raise EdgarError(
            "Set SEC_USER_AGENT to your name and email, for example: "
            "SEC_USER_AGENT='Student Name student@example.edu'."
        )
    return value


def fetch_json(url: str, user_agent: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch one public SEC JSON document with a declared user agent."""
    request = Request(
        url,
        headers={"User-Agent": validate_user_agent(user_agent), "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except HTTPError as exc:
        raise EdgarError(f"SEC EDGAR returned HTTP {exc.code} for {url}.") from exc
    except URLError as exc:
        raise EdgarError(f"Could not reach SEC EDGAR: {exc.reason}.") from exc
    except TimeoutError as exc:
        raise EdgarError("The SEC EDGAR request timed out.") from exc
    except json.JSONDecodeError as exc:
        raise EdgarError("SEC EDGAR did not return readable JSON.") from exc


def lookup_cik(ticker: str, ticker_payload: dict[str, Any]) -> int:
    """Resolve an exact ticker from the SEC ticker-to-CIK file."""
    wanted = ticker.strip().upper()
    for record in ticker_payload.values():
        if str(record.get("ticker", "")).upper() == wanted:
            return int(record["cik_str"])
    raise EdgarError(f"Ticker {wanted!r} was not found in the SEC ticker file.")


def _parse_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _is_one_year_fact(fact: dict[str, Any]) -> bool:
    start = _parse_date(fact.get("start"))
    end = _parse_date(fact.get("end"))
    if not start or not end:
        return False
    duration = (end - start).days + 1
    return FLOW_MIN_DAYS <= duration <= FLOW_MAX_DAYS


def _usd_facts(companyfacts: dict[str, Any], tag: str) -> list[dict[str, Any]]:
    concept = companyfacts.get("facts", {}).get("us-gaap", {}).get(tag, {})
    return list(concept.get("units", {}).get("USD", []))


def _annual_facts(
    companyfacts: dict[str, Any], tag: str, fiscal_end: str | None = None
) -> list[dict[str, Any]]:
    facts = [
        fact
        for fact in _usd_facts(companyfacts, tag)
        if fact.get("form") == "10-K" and _is_one_year_fact(fact)
    ]
    if fiscal_end is not None:
        facts = [fact for fact in facts if fact.get("end") == fiscal_end]
    return facts


def _instant_facts(
    companyfacts: dict[str, Any], tag: str, fiscal_end: str
) -> list[dict[str, Any]]:
    return [
        fact
        for fact in _usd_facts(companyfacts, tag)
        if fact.get("form") == "10-K"
        and fact.get("end") == fiscal_end
        and not fact.get("start")
    ]


def _latest_filed(facts: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = list(facts)
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda fact: (str(fact.get("filed", "")), str(fact.get("accn", ""))),
    )


def _missing(tags: list[str], status: str = "not found") -> dict[str, Any]:
    return {"status": status, "value": None, "tag": " then ".join(tags)}


def _reported(value: float, tag: str) -> dict[str, Any]:
    return {"status": "ok", "value": value, "tag": tag}


def _flow_metric(
    companyfacts: dict[str, Any], metric: str, fiscal_end: str
) -> dict[str, Any]:
    tags = METRIC_TAGS[metric]
    for tag in tags:
        fact = _latest_filed(_annual_facts(companyfacts, tag, fiscal_end))
        if fact is not None:
            return _reported(float(fact["val"]) / 1_000_000.0, tag)
    return _missing(tags)


def _equity_metric(companyfacts: dict[str, Any], fiscal_end: str) -> dict[str, Any]:
    tag = METRIC_TAGS["equity"][0]
    fact = _latest_filed(_instant_facts(companyfacts, tag, fiscal_end))
    if fact is None:
        return _missing([tag])
    return _reported(float(fact["val"]) / 1_000_000.0, tag)


def _fiscal_year_ends(companyfacts: dict[str, Any], years: int = 5) -> list[str]:
    """Use annual 10-K flow periods to identify the latest fiscal-year-end dates."""
    ends: set[str] = set()
    anchor_tags = (
        METRIC_TAGS["revenue"]
        + METRIC_TAGS["net_income"]
        + METRIC_TAGS["operating_cash_flow"]
    )
    for tag in anchor_tags:
        ends.update(str(fact["end"]) for fact in _annual_facts(companyfacts, tag))
    if not ends:
        raise EdgarError("No one-year 10-K flow periods were found in SEC company facts.")
    return sorted(ends)[-years:]


def _computed_metrics(row: dict[str, Any]) -> None:
    net_income = row["net_income"]
    equity = row["equity"]
    if net_income["status"] != "ok" or equity["status"] != "ok":
        row["roe"] = _missing(
            ["NetIncomeLoss / StockholdersEquity"], status="not found"
        )
    elif equity["value"] <= 0:
        row["roe"] = _missing(
            ["NetIncomeLoss / StockholdersEquity"], status="not known"
        )
    else:
        row["roe"] = _reported(
            net_income["value"] / equity["value"] * 100.0,
            "NetIncomeLoss / StockholdersEquity",
        )

    operating_cash_flow = row["operating_cash_flow"]
    capital_spending = row["capital_spending"]
    owner_tag = (
        "NetCashProvidedByUsedInOperatingActivities - "
        f"{capital_spending['tag']}"
    )
    if operating_cash_flow["status"] != "ok" or capital_spending["status"] != "ok":
        row["owner_earnings"] = _missing([owner_tag])
    else:
        row["owner_earnings"] = _reported(
            operating_cash_flow["value"] - capital_spending["value"], owner_tag
        )


def _check_all(rows: list[dict[str, Any]], metric: str, predicate: Any) -> str:
    values = [row[metric] for row in rows]
    if not values or any(cell["status"] != "ok" for cell in values):
        return "not known"
    return "pass" if all(predicate(float(cell["value"])) for cell in values) else "fail"


def compute_checks(rows: list[dict[str, Any]]) -> dict[str, str]:
    """Compute the three course-defined Buffett checks without model judgment."""
    owner_growth = "not known"
    if rows:
        first = rows[0]["owner_earnings"]
        last = rows[-1]["owner_earnings"]
        if first["status"] == "ok" and last["status"] == "ok":
            owner_growth = "pass" if last["value"] > first["value"] else "fail"

    return {
        "roe_15_every_year": _check_all(rows, "roe", lambda value: value >= 15.0),
        "owner_earnings_positive_every_year": _check_all(
            rows, "owner_earnings", lambda value: value > 0.0
        ),
        "owner_earnings_grew": owner_growth,
    }


def analyze_companyfacts(ticker: str, companyfacts: dict[str, Any]) -> dict[str, Any]:
    """Turn SEC company facts into five tagged rows and deterministic checks."""
    rows: list[dict[str, Any]] = []
    for fiscal_end in _fiscal_year_ends(companyfacts):
        row: dict[str, Any] = {"fiscal_year_end": fiscal_end}
        for metric in (
            "revenue",
            "net_income",
            "operating_cash_flow",
            "capital_spending",
        ):
            row[metric] = _flow_metric(companyfacts, metric, fiscal_end)
        row["equity"] = _equity_metric(companyfacts, fiscal_end)
        _computed_metrics(row)
        rows.append(row)

    return {
        "ticker": ticker.strip().upper(),
        "company": companyfacts.get("entityName", "Company name not found"),
        "unit": "USD millions",
        "source": "SEC EDGAR company facts; 10-K only",
        "rows": rows,
        "checks": compute_checks(rows),
    }


def analyze_ticker(ticker: str, user_agent: str) -> dict[str, Any]:
    """Download the ticker map and company facts, then run the analysis."""
    declared_user_agent = validate_user_agent(user_agent)
    ticker_payload = fetch_json(TICKERS_URL, declared_user_agent)
    cik = lookup_cik(ticker, ticker_payload)
    companyfacts = fetch_json(
        COMPANYFACTS_URL.format(cik=cik), declared_user_agent
    )
    result = analyze_companyfacts(ticker, companyfacts)
    result["cik"] = f"{cik:010d}"
    return result


def _format_millions(value: float) -> str:
    if float(value).is_integer():
        return f"{value:,.0f}"
    return f"{value:,.1f}"


def format_cell(cell: dict[str, Any], metric: str) -> str:
    """Format a value and its source tag, preserving explicit gaps."""
    if cell["status"] != "ok":
        return f"{cell['status']} [XBRL: {cell['tag']}]"
    if metric == "roe":
        value = f"{cell['value']:.1f}%"
    else:
        value = _format_millions(float(cell["value"]))
    return f"{value} [XBRL: {cell['tag']}]"


def render_analysis(analysis: dict[str, Any]) -> str:
    """Render every printed number with the XBRL tag(s) that produced it."""
    lines = [
        f"{analysis['ticker']} — {analysis['company']}",
        f"Source: {analysis['source']}",
        f"Units: {analysis['unit']}",
        "",
    ]
    metric_order = (
        "revenue",
        "net_income",
        "operating_cash_flow",
        "capital_spending",
        "equity",
        "roe",
        "owner_earnings",
    )
    for row in analysis["rows"]:
        lines.append(f"Fiscal year end: {row['fiscal_year_end']}")
        for metric in metric_order:
            lines.append(f"  {METRIC_LABELS[metric]}: {format_cell(row[metric], metric)}")
        lines.append("")
    lines.append("Buffett checks (computed in code):")
    for check, label in CHECK_LABELS.items():
        lines.append(f"  {label}: {analysis['checks'][check]}")
    return "\n".join(lines).rstrip() + "\n"


def _normalize_number(token: str) -> tuple[str, bool] | None:
    percent = token.rstrip().endswith("%")
    cleaned = token.replace("$", "").replace(",", "").replace("%", "").strip()
    try:
        number = Decimal(cleaned)
    except InvalidOperation:
        return None
    return (str(number.normalize()), percent)


def audit_memo_numbers(memo: str, script_output: str) -> list[str]:
    """Return memo number literals that do not occur numerically in script output."""
    allowed = {
        normalized
        for token in NUMBER_RE.findall(script_output)
        if (normalized := _normalize_number(token)) is not None
    }
    flagged: list[str] = []
    seen: set[str] = set()
    for token in NUMBER_RE.findall(memo):
        normalized = _normalize_number(token)
        if normalized not in allowed and token not in seen:
            flagged.append(token)
            seen.add(token)
    return flagged


def _load_companyfacts(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EdgarError(f"Could not read company facts from {path}.") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print five years of tagged SEC 10-K facts and Buffett checks."
    )
    parser.add_argument("ticker", help="Public-company ticker, such as COST")
    parser.add_argument(
        "--user-agent",
        help="SEC identity string; defaults to the SEC_USER_AGENT environment variable",
    )
    parser.add_argument(
        "--companyfacts-file",
        type=Path,
        help="Offline validation input; skips all SEC downloads",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.companyfacts_file:
            analysis = analyze_companyfacts(
                args.ticker, _load_companyfacts(args.companyfacts_file)
            )
        else:
            user_agent = args.user_agent or os.environ.get("SEC_USER_AGENT")
            analysis = analyze_ticker(args.ticker, validate_user_agent(user_agent))
    except EdgarError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(analysis, indent=2, sort_keys=True))
    else:
        print(render_analysis(analysis), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
