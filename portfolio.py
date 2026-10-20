"""Price the Lab 14 Meridian baseline portfolios.

Returns, volatilities, correlations, and weights are stored as decimals.
Run from the repository root with: python portfolio.py
"""

from __future__ import annotations

from math import sqrt


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


def reserve_eligible_weight(weights: dict[str, float]) -> float:
    """Return the combined bills and Treasury 10-year note weight."""
    return sum(weights[name] for name in RESERVE_ELIGIBLE)


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
