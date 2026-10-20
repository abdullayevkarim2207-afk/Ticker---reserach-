from __future__ import annotations

from copy import deepcopy
import unittest

import portfolio


class PortfolioTests(unittest.TestCase):
    def setUp(self) -> None:
        portfolio.validate_inputs(portfolio.SLEEVES, portfolio.CORRELATIONS)
        self.covariance = portfolio.build_covariance_matrix(
            portfolio.SLEEVES, portfolio.CORRELATIONS
        )

    def test_known_answers(self) -> None:
        expected = {
            "Benchmark": ("6.80%", "10.46%", "0.0%"),
            "Equal weight": ("5.20%", "5.21%", "50.0%"),
            "Inverse volatility": ("3.77%", "1.05%", "90.3%"),
        }
        for name, weights in portfolio.build_portfolios(portfolio.SLEEVES).items():
            result = (
                f"{portfolio.expected_return(weights, portfolio.SLEEVES):.2%}",
                f"{portfolio.portfolio_volatility(weights, self.covariance):.2%}",
                f"{portfolio.reserve_eligible_weight(weights):.1%}",
            )
            self.assertEqual(result, expected[name])

    def test_changed_correlation_raises_benchmark_volatility(self) -> None:
        correlations = deepcopy(portfolio.CORRELATIONS)
        correlations["Investment-grade bond fund"][
            "Global equity index fund"
        ] = 0.50
        correlations["Global equity index fund"][
            "Investment-grade bond fund"
        ] = 0.50
        portfolio.validate_inputs(portfolio.SLEEVES, correlations)
        covariance = portfolio.build_covariance_matrix(portfolio.SLEEVES, correlations)
        weights = portfolio.benchmark_weights(portfolio.SLEEVES)
        self.assertAlmostEqual(
            portfolio.portfolio_volatility(weights, covariance), 0.1100, places=4
        )

    def test_bad_correlation_is_refused(self) -> None:
        correlations = deepcopy(portfolio.CORRELATIONS)
        correlations["Investment-grade bond fund"][
            "Global equity index fund"
        ] = 1.30
        with self.assertRaisesRegex(ValueError, "between -1 and 1"):
            portfolio.validate_inputs(portfolio.SLEEVES, correlations)

    def test_asymmetric_table_is_refused(self) -> None:
        correlations = deepcopy(portfolio.CORRELATIONS)
        correlations["Investment-grade bond fund"][
            "Global equity index fund"
        ] = 0.50
        with self.assertRaisesRegex(ValueError, "not symmetric"):
            portfolio.validate_inputs(portfolio.SLEEVES, correlations)


if __name__ == "__main__":
    unittest.main()
