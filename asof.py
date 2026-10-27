"""Build an as-of panel and compare it with a look-ahead-biased panel."""

from datetime import date
from typing import Iterable


# Editable inputs -----------------------------------------------------------
DECISION_DATE = "2026-03-31"

TABLE = [
    {"row": 1, "ticker": "AAA", "month": "2026-01", "published": "2026-02-10", "index": 101.0},
    {"row": 2, "ticker": "AAA", "month": "2026-02", "published": "2026-03-10", "index": 104.0},
    {"row": 3, "ticker": "AAA", "month": "2026-03", "published": "2026-04-10", "index": 109.0},
    {"row": 4, "ticker": "AAA", "month": "2026-02", "published": "2026-03-25", "index": 103.0},
    {"row": 5, "ticker": "BBB", "month": "2026-01", "published": "2026-02-10", "index": 98.0},
    {"row": 6, "ticker": "BBB", "month": "2026-02", "published": "2026-03-10", "index": 97.0},
    {"row": 7, "ticker": "BBB", "month": "2026-02", "published": "2026-03-10", "index": 97.0},
    {"row": 8, "ticker": "BBB", "month": "2026-03", "published": "2026-04-10", "index": 92.0},
    {"row": 9, "ticker": "CCC", "month": "2026-01", "published": "2026-02-10", "index": 110.0},
    {"row": 10, "ticker": "CCC", "month": "2026-02", "published": "2026-04-05", "index": 112.0},
    {"row": 11, "ticker": "", "month": "2026-02", "published": "2026-03-10", "index": 99.0},
    {"row": 12, "ticker": "CCC", "month": "2026-02", "published": "2026-03-10", "index": 111.0},
]


def row_numbers(rows: Iterable[dict]) -> str:
    """Return source row numbers in a compact, readable form."""
    numbers = [str(row["row"]) for row in rows]
    return ", ".join(numbers) if numbers else "none"


def quarantine_missing_tickers(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Rule 1: set aside rows whose ticker is empty or whitespace."""
    removed = [row for row in rows if not row["ticker"].strip()]
    kept = [row for row in rows if row["ticker"].strip()]
    return kept, removed


def remove_exact_duplicates(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Rule 2: keep the first row for each exact data record."""
    kept = []
    removed = []
    seen = set()

    for row in rows:
        # The source row number identifies the record; it is not part of its data.
        identity = (row["ticker"], row["month"], row["published"], row["index"])
        if identity in seen:
            removed.append(row)
        else:
            seen.add(identity)
            kept.append(row)
    return kept, removed


def remove_late_publications(
    rows: list[dict], decision_date: date
) -> tuple[list[dict], list[dict]]:
    """Rule 3: remove information that was not public by the decision date."""
    kept = []
    removed = []
    for row in rows:
        if date.fromisoformat(row["published"]) <= decision_date:
            kept.append(row)
        else:
            removed.append(row)
    return kept, removed


def keep_latest_vintage(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Rule 4: retain the latest publication for each ticker-month pair."""
    latest_by_ticker_month = {}

    # Comparing ISO publication dates works chronologically because they use
    # YYYY-MM-DD format. The row number breaks a same-day tie deterministically.
    for row in rows:
        key = (row["ticker"], row["month"])
        current = latest_by_ticker_month.get(key)
        if current is None or (row["published"], row["row"]) > (
            current["published"],
            current["row"],
        ):
            latest_by_ticker_month[key] = row

    kept_ids = {row["row"] for row in latest_by_ticker_month.values()}
    kept = [row for row in rows if row["row"] in kept_ids]
    removed = [row for row in rows if row["row"] not in kept_ids]
    return kept, removed


def build_asof_panel(
    table: list[dict], decision_date_text: str
) -> tuple[list[dict], list[tuple[str, list[dict]]]]:
    """Apply all four rules in order and return the panel and audit funnel."""
    decision_date = date.fromisoformat(decision_date_text)
    rows, missing = quarantine_missing_tickers(table)
    rows, duplicates = remove_exact_duplicates(rows)
    rows, late = remove_late_publications(rows, decision_date)
    rows, older_vintages = keep_latest_vintage(rows)
    funnel = [
        ("Quarantined: no ticker", missing),
        ("Exact duplicate", duplicates),
        (f"Published after {decision_date.isoformat()}", late),
        ("Older vintage replaced by a revision", older_vintages),
    ]
    return rows, funnel


def build_naive_panel(table: list[dict]) -> list[dict]:
    """Build today's panel without imposing a historical decision date."""
    rows, _ = quarantine_missing_tickers(table)
    rows, _ = remove_exact_duplicates(rows)
    rows, _ = keep_latest_vintage(rows)
    return rows


def calculate_signals(rows: list[dict]) -> dict[str, dict]:
    """Calculate latest-month changes from the immediately preceding month."""
    by_ticker: dict[str, list[dict]] = {}
    for row in rows:
        by_ticker.setdefault(row["ticker"], []).append(row)

    signals = {}
    for ticker, ticker_rows in sorted(by_ticker.items()):
        ordered = sorted(ticker_rows, key=lambda row: row["month"])
        if len(ordered) < 2:
            signals[ticker] = {"value": None, "month": ordered[-1]["month"]}
            continue
        previous, latest = ordered[-2:]
        change = (latest["index"] / previous["index"] - 1.0) * 100.0
        signals[ticker] = {
            "value": change,
            "month": latest["month"],
            "row": latest["row"],
        }
    return signals


def month_name(month_text: str) -> str:
    """Convert YYYY-MM into the English month name without external packages."""
    names = (
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    )
    return names[int(month_text[5:7]) - 1]


def revised_months(table: list[dict]) -> set[tuple[str, str]]:
    """Identify ticker-months with more than one nonduplicate publication."""
    rows, _ = quarantine_missing_tickers(table)
    rows, _ = remove_exact_duplicates(rows)
    counts: dict[tuple[str, str], int] = {}
    for row in rows:
        key = (row["ticker"], row["month"])
        counts[key] = counts.get(key, 0) + 1
    return {key for key, count in counts.items() if count > 1}


def format_signal(
    ticker: str,
    signal: dict,
    revisions: set[tuple[str, str]],
    show_revision: bool = False,
) -> str:
    """Format one calculated signal to the precision required by the lab."""
    if signal["value"] is None:
        return "not enough months"
    label = month_name(signal["month"])
    if show_revision and (ticker, signal["month"]) in revisions:
        label += ", revised"
    return f'{signal["value"]:+.2f}% ({label})'


def print_panel(rows: list[dict]) -> None:
    """Print a small fixed-width table without third-party dependencies."""
    print("Row  Ticker  Month measured  Published on  Index")
    for row in sorted(rows, key=lambda item: item["row"]):
        print(
            f'{row["row"]:>3}  {row["ticker"]:<6}  {row["month"]:<14}  '
            f'{row["published"]:<12}  {row["index"]:.1f}'
        )


def main() -> None:
    asof_panel, funnel = build_asof_panel(TABLE, DECISION_DATE)
    naive_panel = build_naive_panel(TABLE)
    revisions = revised_months(TABLE)

    print(f"Decision date: {DECISION_DATE}\n")
    print("ROW FUNNEL")
    for label, removed in funnel:
        print(f"- {label}: removed {len(removed)} row(s) [{row_numbers(removed)}]")
    print(f"- As-of panel: {len(asof_panel)} row(s) [{row_numbers(asof_panel)}]")

    print("\nAS-OF PANEL")
    print_panel(asof_panel)

    asof_signals = calculate_signals(asof_panel)
    naive_signals = calculate_signals(naive_panel)
    print("\nSIGNALS")
    print("Ticker  As-of signal              Naive signal")
    for ticker in sorted(set(asof_signals) | set(naive_signals)):
        asof_text = format_signal(ticker, asof_signals[ticker], revisions)
        naive_text = format_signal(
            ticker, naive_signals[ticker], revisions, show_revision=True
        )
        print(f"{ticker:<6}  {asof_text:<25} {naive_text}")


if __name__ == "__main__":
    main()
