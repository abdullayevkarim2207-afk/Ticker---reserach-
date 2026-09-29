"""Lab 08 reported P/E check for Ford Motor Company.

The calculator deliberately refuses to produce an implied Ford share value when
Ford's annual reported diluted EPS is zero or negative.
"""

from __future__ import annotations

import argparse
import csv
import statistics
from datetime import date
from pathlib import Path


INPUT_FILE = Path(__file__).with_name("lab08_inputs.csv")
ADMITTED_DECISIONS = {"use", "qualify"}


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_rows(rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("The input file is empty.")

    targets = [row for row in rows if row["role"] == "target"]
    if len(targets) != 1:
        raise ValueError("Provide exactly one target row.")

    price_dates = {row["price_date"] for row in rows}
    currencies = {row["currency"] for row in rows}
    if len(price_dates) != 1:
        raise ValueError("Target and peer prices must have the same date.")
    if len(currencies) != 1:
        raise ValueError("This lab file requires a common price/EPS currency basis.")

    comparison_date = date.fromisoformat(targets[0]["price_date"])
    for row in rows:
        if date.fromisoformat(row["earnings_publication_date"]) > comparison_date:
            raise ValueError(
                f"{row['ticker']} earnings were not public by the comparison date."
            )
        if float(row["closing_price"]) <= 0:
            raise ValueError(f"{row['ticker']} price must be positive.")


def peer_multiples(
    rows: list[dict[str, str]], removed_ticker: str | None = None
) -> list[tuple[str, float]]:
    multiples: list[tuple[str, float]] = []
    for row in rows:
        if row["role"] != "peer" or row["decision"] not in ADMITTED_DECISIONS:
            continue
        if removed_ticker and row["ticker"].upper() == removed_ticker.upper():
            continue
        eps = float(row["annual_reported_diluted_eps"])
        if eps <= 0:
            print(f"Excluded from P/E calculation: {row['ticker']} has EPS {eps:.2f}.")
            continue
        multiple = float(row["closing_price"]) / eps
        multiples.append((row["ticker"], multiple))
    return multiples


def print_result(rows: list[dict[str, str]], removed_ticker: str | None) -> None:
    target = next(row for row in rows if row["role"] == "target")
    multiples = peer_multiples(rows, removed_ticker)

    print(
        f"Target: {target['company']} ({target['ticker']}); "
        f"comparison date: {target['price_date']}"
    )
    print(
        f"Target close: ${float(target['closing_price']):.2f}; "
        f"FY2025 reported diluted EPS: ${float(target['annual_reported_diluted_eps']):.2f}"
    )
    if removed_ticker:
        print(f"Changed-peer case: removed {removed_ticker.upper()}")

    for ticker, multiple in multiples:
        print(f"{ticker} reported P/E: {multiple:.6f}x")

    if not multiples:
        print("Peer reference multiple: unavailable; no usable admitted peers remain.")
    elif len(multiples) == 1:
        print(f"Single-peer reference multiple: {multiples[0][1]:.6f}x")
    else:
        values = [multiple for _, multiple in multiples]
        print(f"Peer P/E range: {min(values):.6f}x to {max(values):.6f}x")
        print(f"Peer median P/E: {statistics.median(values):.6f}x")

    target_eps = float(target["annual_reported_diluted_eps"])
    if target_eps <= 0:
        print(
            "Ford implied share value: UNUSABLE. Reported annual diluted EPS is "
            "zero or negative, so P/E cannot support a valuation."
        )
        return

    values = [multiple for _, multiple in multiples]
    if len(values) == 1:
        print(f"Ford single-peer implied value: ${target_eps * values[0]:.2f}")
    elif values:
        print(
            "Ford peer-implied range: "
            f"${target_eps * min(values):.2f} to ${target_eps * max(values):.2f}"
        )
        print(
            "Ford median-implied value: "
            f"${target_eps * statistics.median(values):.2f}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--remove",
        metavar="TICKER",
        help="Run the changed-peer check after removing one admitted peer.",
    )
    args = parser.parse_args()
    rows = load_rows(INPUT_FILE)
    validate_rows(rows)
    print_result(rows, args.remove)


if __name__ == "__main__":
    main()
