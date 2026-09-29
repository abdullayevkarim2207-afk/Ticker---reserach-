"""Lab 07: Asbury comparable-company P/E calculation.

The case pairs December 31, 2024 closing prices with FY2024 total GAAP
diluted EPS. It is a retrospective training comparison, not a live valuation.
"""

from statistics import median


# Editable inputs
TARGET = {
    "ticker": "ABG",
    "name": "Asbury Automotive",
    "price": 243.03,
    "diluted_eps": 21.50,
}

PEERS = [
    {
        "ticker": "AN",
        "name": "AutoNation",
        "price": 169.84,
        "diluted_eps": 16.92,
    },
    {
        "ticker": "GPI",
        "name": "Group 1 Automotive",
        "price": 421.48,
        "diluted_eps": 36.81,
    },
]


def positive_number(value):
    """Return True when value is a positive int or float (but not a bool)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def prepare_peers(peers, target_ticker):
    """Exclude the target and duplicate tickers, keeping the first peer entry."""
    prepared = []
    excluded = []
    seen = set()
    normalized_target = str(target_ticker).strip().upper()

    for peer in peers:
        ticker = str(peer.get("ticker", "")).strip().upper()
        if ticker == normalized_target:
            excluded.append(f"{ticker or '[missing ticker]'}: target company excluded")
        elif not ticker:
            excluded.append("[missing ticker]: peer excluded")
        elif ticker in seen:
            excluded.append(f"{ticker}: duplicate peer excluded")
        else:
            seen.add(ticker)
            prepared.append(peer)

    return prepared, excluded


def calculate_pe(peer):
    """Return price divided by diluted EPS, or None if the inputs are unusable."""
    price = peer.get("price")
    diluted_eps = peer.get("diluted_eps")
    if not positive_number(price) or not positive_number(diluted_eps):
        return None
    return price / diluted_eps


def print_implied_values(peer_multiples, target_eps):
    """Print the full-peer P/E result and return the unrounded median estimate."""
    print("\nAsbury implied prices")
    if not positive_number(target_eps):
        print("Not meaningful: target diluted EPS is missing or nonpositive.")
        return None

    multiples = [multiple for _, multiple in peer_multiples]
    if not multiples:
        print("No usable peers; no estimate.")
        return None

    median_multiple = median(multiples)
    median_price = median_multiple * target_eps

    if len(multiples) == 1:
        print(f"Reference P/E: {multiples[0]:.6f}x")
        print(f"Reference estimate: ${median_price:.2f} (one valid peer; no range)")
    else:
        minimum_price = min(multiples) * target_eps
        maximum_price = max(multiples) * target_eps
        print(f"Minimum peer P/E: {min(multiples):.6f}x")
        print(f"Median peer P/E: {median_multiple:.6f}x")
        print(f"Maximum peer P/E: {max(multiples):.6f}x")
        print(f"Implied range: ${minimum_price:.2f}-${maximum_price:.2f}")
        print(f"Median-implied price: ${median_price:.2f}")

    return median_price


def print_leave_one_out(peer_multiples, target_eps, full_peer_estimate):
    """Print the effect of removing each usable peer, using unrounded values."""
    print("\nLeave-one-peer-out analysis")
    if full_peer_estimate is None or not positive_number(target_eps):
        print("No full-peer estimate; leave-one-out changes are not meaningful.")
        return

    for removed_ticker, _ in peer_multiples:
        remaining = [
            multiple
            for ticker, multiple in peer_multiples
            if ticker != removed_ticker
        ]
        if not remaining:
            print(f"Remove {removed_ticker}: no estimate; no usable peers remain.")
            continue

        remaining_estimate = median(remaining) * target_eps
        change = remaining_estimate - full_peer_estimate
        estimate_kind = "reference estimate; no range" if len(remaining) == 1 else "median estimate"
        print(
            f"Remove {removed_ticker}: ${remaining_estimate:.2f} "
            f"({estimate_kind}); change from full-peer estimate: {change:+.2f}"
        )


def main():
    prepared_peers, excluded = prepare_peers(PEERS, TARGET["ticker"])

    print("Lab 07 - Comparable-Company P/E")
    print("Basis: December 31, 2024 closing price / FY2024 total GAAP diluted EPS")
    print(f"Target: {TARGET['name']} ({TARGET['ticker']})")

    if excluded:
        print("\nExcluded entries")
        for reason in excluded:
            print(f"- {reason}")

    print("\nPeer P/E multiples")
    peer_multiples = []
    for peer in prepared_peers:
        ticker = str(peer["ticker"]).strip().upper()
        multiple = calculate_pe(peer)
        if multiple is None:
            print(
                f"{peer.get('name', ticker)} ({ticker}): not meaningful; "
                "price or diluted EPS is missing or nonpositive."
            )
        else:
            peer_multiples.append((ticker, multiple))
            print(f"{peer['name']} ({ticker}): {multiple:.6f}x")

    full_peer_estimate = print_implied_values(
        peer_multiples, TARGET.get("diluted_eps")
    )
    print_leave_one_out(
        peer_multiples, TARGET.get("diluted_eps"), full_peer_estimate
    )
    print("\nNo cash/debt bridge is used because P/E is an equity multiple.")


if __name__ == "__main__":
    main()
