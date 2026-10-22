from __future__ import annotations

from copy import deepcopy
from io import StringIO
from pathlib import Path
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

    def test_search_reproduces_meridian_loaded_answer(self) -> None:
        weights = portfolio.search_lowest_risk_mix(
            portfolio.SLEEVES,
            portfolio.CORRELATIONS,
            0.065,
            portfolio.RESERVE_ELIGIBLE,
            0.03,
        )
        self.assertIsNotNone(weights)
        self.assertEqual(
            [f"{weights[name]:.0%}" for name in portfolio.SLEEVES],
            ["0%", "20%", "25%", "55%"],
        )
        covariance = portfolio.build_covariance_matrix(
            portfolio.SLEEVES, portfolio.CORRELATIONS
        )
        self.assertEqual(f"{portfolio.expected_return(weights, portfolio.SLEEVES):.2%}", "6.51%")
        self.assertEqual(f"{portfolio.portfolio_volatility(weights, covariance):.2%}", "9.44%")

    def test_one_point_equity_change_moves_25_points(self) -> None:
        changed = deepcopy(portfolio.SLEEVES)
        changed["Global equity index fund"]["expected_return"] = 0.07
        weights = portfolio.search_lowest_risk_mix(
            changed,
            portfolio.CORRELATIONS,
            0.065,
            portfolio.RESERVE_ELIGIBLE,
            0.03,
        )
        self.assertIsNotNone(weights)
        self.assertEqual(
            [f"{weights[name]:.0%}" for name in changed],
            ["0%", "10%", "10%", "80%"],
        )
        covariance = portfolio.build_covariance_matrix(
            changed, portfolio.CORRELATIONS
        )
        self.assertEqual(f"{portfolio.expected_return(weights, changed):.2%}", "6.53%")
        self.assertEqual(f"{portfolio.portfolio_volatility(weights, covariance):.2%}", "12.94%")

    def test_search_moves_when_engine_correlation_changes(self) -> None:
        correlations = deepcopy(portfolio.CORRELATIONS)
        correlations["Investment-grade bond fund"]["Global equity index fund"] = 0.50
        correlations["Global equity index fund"]["Investment-grade bond fund"] = 0.50
        weights = portfolio.search_lowest_risk_mix(
            portfolio.SLEEVES,
            correlations,
            0.065,
            portfolio.RESERVE_ELIGIBLE,
            0.03,
        )
        self.assertIsNotNone(weights)
        self.assertEqual(
            [f"{weights[name]:.0%}" for name in portfolio.SLEEVES],
            ["0%", "40%", "0%", "60%"],
        )
        covariance = portfolio.build_covariance_matrix(portfolio.SLEEVES, correlations)
        self.assertEqual(f"{portfolio.expected_return(weights, portfolio.SLEEVES):.2%}", "6.52%")
        self.assertEqual(f"{portfolio.portfolio_volatility(weights, covariance):.2%}", "9.73%")

    def test_price_csv_estimates_all_and_last_36_returns(self) -> None:
        rows = ["Date,A,B"]
        for month in range(1, 39):
            year = 2020 + (month - 1) // 12
            month_number = (month - 1) % 12 + 1
            rows.append(
                f"{year:04d}-{month_number:02d}-01,{100 + month},{200 + 2 * month + (month % 2)}"
            )
        csv_text = "\n".join(rows)
        all_sleeves, all_correlations = portfolio.estimate_from_price_csv(
            StringIO(csv_text)
        )
        recent_sleeves, recent_correlations = portfolio.estimate_from_price_csv(
            StringIO(csv_text), last_36_months=True
        )
        self.assertEqual(set(all_sleeves), {"A", "B"})
        self.assertEqual(set(recent_sleeves), {"A", "B"})
        self.assertEqual(all_correlations["A"]["A"], 1.0)
        self.assertEqual(recent_correlations["B"]["B"], 1.0)
        self.assertNotEqual(
            all_sleeves["A"]["expected_return"],
            recent_sleeves["A"]["expected_return"],
        )

    def test_project_two_price_file_stability_answers(self) -> None:
        price_file = Path(__file__).parent.parent / "prices.csv"
        answers = {}
        for recent in (False, True):
            sleeves, correlations = portfolio.estimate_from_price_csv(
                price_file, last_36_months=recent
            )
            answers[recent] = portfolio.search_lowest_risk_mix(
                sleeves,
                correlations,
                0.065,
                {"SGOV", "VGIT"},
                0.03,
            )
        self.assertEqual(
            [f"{answers[False][name]:.0%}" for name in answers[False]],
            ["65%", "0%", "0%", "35%"],
        )
        self.assertEqual(
            [f"{answers[True][name]:.0%}" for name in answers[True]],
            ["85%", "0%", "0%", "15%"],
        )
        largest_change = max(
            abs(answers[True][name] - answers[False][name])
            for name in answers[False]
        )
        self.assertAlmostEqual(largest_change, 0.20)

    def test_project_two_one_point_vt_sensitivity(self) -> None:
        price_file = Path(__file__).parent.parent / "prices.csv"
        sleeves, correlations = portfolio.estimate_from_price_csv(price_file)
        loaded = portfolio.search_lowest_risk_mix(
            sleeves, correlations, 0.065, {"SGOV", "VGIT"}, 0.03
        )
        changed = deepcopy(sleeves)
        changed["VT"]["expected_return"] -= 0.01
        attacked = portfolio.search_lowest_risk_mix(
            changed, correlations, 0.065, {"SGOV", "VGIT"}, 0.03
        )
        self.assertEqual(
            [f"{attacked[name]:.0%}" for name in attacked],
            ["60%", "0%", "0%", "40%"],
        )
        largest_change = max(
            abs(attacked[name] - loaded[name]) for name in loaded
        )
        self.assertAlmostEqual(largest_change, 0.05)


if __name__ == "__main__":
    unittest.main()
