"""Price the Lab 14 Meridian baseline portfolios.

Returns, volatilities, correlations, and weights are stored as decimals.
Run from the repository root with: python portfolio.py
"""

from __future__ import annotations

import csv
from datetime import date
from io import StringIO
from math import sqrt
from pathlib import Path
from statistics import correlation, mean, stdev
from typing import IO, Iterator


# Editable inputs: course-authored training values, not market estimates.
SLEEVES = {
    "Treasury bills": {"expected_return": 0.035, "volatility": 0.005},
    "Treasury 10-year note": {"expected_return": 0.043, "volatility": 0.070},
    "Investment-grade bond fund": {
        "expected_return": 0.050,
        "volatility": 0.060,
    },
    "Global equity index fund": {"expected_return": 0.080, "volatility": 0.160},
}

CORRELATIONS = {
    "Treasury bills": {
        "Treasury bills": 1.00,
        "Treasury 10-year note": 0.10,
        "Investment-grade bond fund": 0.05,
        "Global equity index fund": 0.00,
    },
    "Treasury 10-year note": {
        "Treasury bills": 0.10,
        "Treasury 10-year note": 1.00,
        "Investment-grade bond fund": 0.80,
        "Global equity index fund": -0.10,
    },
    "Investment-grade bond fund": {
        "Treasury bills": 0.05,
        "Treasury 10-year note": 0.80,
        "Investment-grade bond fund": 1.00,
        "Global equity index fund": 0.25,
    },
    "Global equity index fund": {
        "Treasury bills": 0.00,
        "Treasury 10-year note": -0.10,
        "Investment-grade bond fund": 0.25,
        "Global equity index fund": 1.00,
    },
}

OBJECTIVE_RETURN = 0.065
RESERVE_ELIGIBLE = {"Treasury bills", "Treasury 10-year note"}


def validate_inputs(
    sleeves: dict[str, dict[str, float]],
    correlations: dict[str, dict[str, float]],
) -> None:
    """Refuse invalid or incomplete correlation inputs with a clear message."""
    names = set(sleeves)
    if set(correlations) != names:
        raise ValueError("Correlation rows must exactly match the sleeve names.")

    for name, inputs in sleeves.items():
        if inputs["volatility"] <= 0.0:
            raise ValueError(f"Volatility for {name} must be greater than zero.")

    for row_name, row in correlations.items():
        if set(row) != names:
            raise ValueError(
                f"Correlation columns for {row_name} must exactly match the sleeve names."
            )
        for column_name, correlation in row.items():
            if not -1.0 <= correlation <= 1.0:
                raise ValueError(
                    f"Correlation for {row_name} and {column_name} must be between "
                    f"-1 and 1; received {correlation}."
                )
            reverse = correlations[column_name][row_name]
            if correlation != reverse:
                raise ValueError(
                    f"Correlation table is not symmetric for {row_name} and "
                    f"{column_name}: {correlation} != {reverse}."
                )


def build_covariance_matrix(
    sleeves: dict[str, dict[str, float]],
    correlations: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
    """Return covariance = correlation * volatility * volatility."""
    return {
        row_name: {
            column_name: (
                correlations[row_name][column_name]
                * sleeves[row_name]["volatility"]
                * sleeves[column_name]["volatility"]
            )
            for column_name in sleeves
        }
        for row_name in sleeves
    }


def benchmark_weights(sleeves: dict[str, dict[str, float]]) -> dict[str, float]:
    """Return the 40% investment-grade bond / 60% global equity benchmark."""
    weights = {name: 0.0 for name in sleeves}
    weights["Investment-grade bond fund"] = 0.40
    weights["Global equity index fund"] = 0.60
    return weights


def equal_weights(sleeves: dict[str, dict[str, float]]) -> dict[str, float]:
    """Return an equal allocation across all sleeves."""
    weight = 1.0 / len(sleeves)
    return {name: weight for name in sleeves}


def inverse_volatility_weights(
    sleeves: dict[str, dict[str, float]],
) -> dict[str, float]:
    """Scale each sleeve's inverse volatility so the weights sum to one."""
    inverse_volatilities = {
        name: 1.0 / inputs["volatility"] for name, inputs in sleeves.items()
    }
    total = sum(inverse_volatilities.values())
    return {name: inverse_volatilities[name] / total for name in sleeves}


def expected_return(
    weights: dict[str, float], sleeves: dict[str, dict[str, float]]
) -> float:
    """Return the weighted expected portfolio return."""
    return sum(
        weights[name] * sleeves[name]["expected_return"] for name in sleeves
    )


def portfolio_variance(
    weights: dict[str, float], covariance: dict[str, dict[str, float]]
) -> float:
    """Return w'Cov(w), including every cross-asset covariance term."""
    return sum(
        weights[row_name] * weights[column_name] * covariance[row_name][column_name]
        for row_name in weights
        for column_name in weights
    )


def portfolio_volatility(
    weights: dict[str, float], covariance: dict[str, dict[str, float]]
) -> float:
    """Return portfolio volatility as the square root of portfolio variance."""
    return sqrt(portfolio_variance(weights, covariance))


def reserve_eligible_weight(
    weights: dict[str, float], reserve_eligible: set[str] | None = None
) -> float:
    """Return the combined weight of the selected reserve-eligible assets."""
    eligible = RESERVE_ELIGIBLE if reserve_eligible is None else reserve_eligible
    return sum(weights.get(name, 0.0) for name in eligible)


def meets_objective(portfolio_return: float, objective_return: float) -> bool:
    """Return whether expected return is at least the stated objective."""
    return portfolio_return >= objective_return


def build_portfolios(
    sleeves: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
    """Return all three Lab 14 baseline weight sets."""
    return {
        "Benchmark": benchmark_weights(sleeves),
        "Equal weight": equal_weights(sleeves),
        "Inverse volatility": inverse_volatility_weights(sleeves),
    }


def _weight_combinations(asset_count: int, units: int) -> Iterator[tuple[int, ...]]:
    """Yield every long-only integer combination whose units sum to the total."""
    if asset_count == 1:
        yield (units,)
        return
    for first in range(units + 1):
        for remainder in _weight_combinations(asset_count - 1, units - first):
            yield (first, *remainder)


def search_lowest_risk_mix(
    sleeves: dict[str, dict[str, float]],
    correlations: dict[str, dict[str, float]],
    objective_return: float,
    reserve_eligible: set[str],
    reserve_minimum: float,
    step: float = 0.05,
) -> dict[str, float] | None:
    """Return the least-volatile feasible long-only mix, or ``None``.

    The search evaluates every fully invested mix on the requested weight grid.
    Expected return and reserve weight must each meet their minimum.
    """
    validate_inputs(sleeves, correlations)
    if not 0.0 < step <= 1.0:
        raise ValueError("The search step must be greater than 0 and at most 1.")
    units = round(1.0 / step)
    if abs(units * step - 1.0) > 1e-10:
        raise ValueError("The search step must divide 100% into equal units.")
    if not 0.0 <= reserve_minimum <= 1.0:
        raise ValueError("The reserve minimum must be between 0% and 100%.")
    unknown = reserve_eligible - set(sleeves)
    if unknown:
        raise ValueError(f"Unknown reserve-eligible assets: {sorted(unknown)}")

    names = list(sleeves)
    covariance = build_covariance_matrix(sleeves, correlations)
    best_weights: dict[str, float] | None = None
    best_volatility = float("inf")

    for combination in _weight_combinations(len(names), units):
        weights = {
            name: unit_count / units
            for name, unit_count in zip(names, combination)
        }
        if expected_return(weights, sleeves) + 1e-12 < objective_return:
            continue
        if (
            reserve_eligible_weight(weights, reserve_eligible) + 1e-12
            < reserve_minimum
        ):
            continue
        volatility = portfolio_volatility(weights, covariance)
        if volatility < best_volatility - 1e-12:
            best_weights = weights
            best_volatility = volatility

    return best_weights


def _read_price_csv(source: str | Path | IO[str] | IO[bytes]) -> str:
    """Read a price CSV path or uploaded file into text."""
    if hasattr(source, "read"):
        content = source.read()
        if hasattr(source, "seek"):
            source.seek(0)
        return content.decode("utf-8-sig") if isinstance(content, bytes) else content
    return Path(source).read_text(encoding="utf-8-sig")


def estimate_from_price_csv(
    source: str | Path | IO[str] | IO[bytes], last_36_months: bool = False
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    """Estimate annualized inputs from oldest-first monthly adjusted prices.

    Arithmetic monthly means are multiplied by 12; sample monthly standard
    deviations are multiplied by square root of 12. If requested, the final 36
    monthly returns (37 prices) are used. These historical estimates are not
    forecasts.
    """
    reader = csv.DictReader(StringIO(_read_price_csv(source)))
    if not reader.fieldnames or len(reader.fieldnames) < 2:
        raise ValueError("CSV must have a date first and at least one ticker.")
    if reader.fieldnames[0].strip().lower() != "date":
        raise ValueError("The first CSV column must be Date.")
    tickers = reader.fieldnames[1:]
    if len(set(tickers)) != len(tickers):
        raise ValueError("Ticker columns must have unique names.")

    dates: list[date] = []
    prices = {ticker: [] for ticker in tickers}
    for row_number, row in enumerate(reader, start=2):
        try:
            dates.append(date.fromisoformat(row[reader.fieldnames[0]].strip()))
            for ticker in tickers:
                price = float(row[ticker])
                if price <= 0.0:
                    raise ValueError
                prices[ticker].append(price)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"CSV row {row_number} must contain an ISO date and positive prices."
            ) from exc

    if len(dates) < 3:
        raise ValueError("CSV must contain at least three monthly price rows.")
    if any(later <= earlier for earlier, later in zip(dates, dates[1:])):
        raise ValueError("CSV dates must be unique and oldest first.")

    monthly_returns = {
        ticker: [
            current / previous - 1.0
            for previous, current in zip(values, values[1:])
        ]
        for ticker, values in prices.items()
    }
    if last_36_months:
        if len(dates) < 37:
            raise ValueError("Last-36 analysis requires at least 37 monthly prices.")
        monthly_returns = {
            ticker: values[-36:] for ticker, values in monthly_returns.items()
        }

    sleeves = {
        ticker: {
            "expected_return": mean(returns) * 12.0,
            "volatility": stdev(returns) * sqrt(12.0),
        }
        for ticker, returns in monthly_returns.items()
    }
    correlations = {
        row_ticker: {
            column_ticker: (
                1.0
                if row_ticker == column_ticker
                else correlation(
                    monthly_returns[row_ticker], monthly_returns[column_ticker]
                )
            )
            for column_ticker in tickers
        }
        for row_ticker in tickers
    }
    validate_inputs(sleeves, correlations)
    return sleeves, correlations


def print_portfolio(
    name: str,
    weights: dict[str, float],
    sleeves: dict[str, dict[str, float]],
    covariance: dict[str, dict[str, float]],
    objective_return: float,
) -> None:
    """Calculate and print one baseline portfolio."""
    portfolio_return = expected_return(weights, sleeves)
    volatility = portfolio_volatility(weights, covariance)
    reserve_weight = reserve_eligible_weight(weights)

    print(f"\n{name}")
    print("  Weights:")
    for sleeve_name, weight in weights.items():
        print(f"    {sleeve_name}: {weight:.1%}")
    print(f"  Expected return: {portfolio_return:.2%}")
    print(f"  Volatility: {volatility:.2%}")
    print(f"  Reserve-eligible weight: {reserve_weight:.1%}")
    print(
        f"  Meets {objective_return:.1%} objective: "
        f"{'yes' if meets_objective(portfolio_return, objective_return) else 'no'}"
    )


def main() -> None:
    """Validate the inputs, build the covariance matrix, and price each baseline."""
    validate_inputs(SLEEVES, CORRELATIONS)
    covariance = build_covariance_matrix(SLEEVES, CORRELATIONS)
    print(f"Objective return: {OBJECTIVE_RETURN:.1%}")
    for name, weights in build_portfolios(SLEEVES).items():
        print_portfolio(name, weights, SLEEVES, covariance, OBJECTIVE_RETURN)


if __name__ == "__main__":
    main()
