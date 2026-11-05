#!/usr/bin/env python3
"""Run the Lab 19 Burry checks on the shared SEC 10-K evidence."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


SHARED_SCRIPTS = Path(__file__).resolve().parents[2] / "buffett-10k" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

from buffett_10k import (  # noqa: E402
    BURRY_CHECK_LABELS,
    analyze_ticker,
    format_cell,
    validate_user_agent,
)


def render_burry(analysis: dict) -> str:
    """Print Burry's required inputs and coded checks."""
    lines = [f"Burry screen — {analysis['ticker']} — {analysis['company']}"]
    for row in analysis["rows"]:
        lines.append(f"Fiscal year end: {row['fiscal_year_end']}")
        lines.append(
            "  Operating cash flow: "
            + format_cell(row["operating_cash_flow"], "operating_cash_flow")
        )
        lines.append(f"  Net income: {format_cell(row['net_income'], 'net_income')}")
        lines.append(
            "  Liabilities / equity: "
            + format_cell(row["liabilities_to_equity"], "liabilities_to_equity")
        )
    lines.append("Burry checks:")
    for key, label in BURRY_CHECK_LABELS.items():
        lines.append(f"  {label}: {analysis['panel_checks']['Burry'][key]}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker")
    parser.add_argument("--user-agent")
    args = parser.parse_args()
    user_agent = validate_user_agent(args.user_agent or os.environ.get("SEC_USER_AGENT"))
    print(render_burry(analyze_ticker(args.ticker, user_agent)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
