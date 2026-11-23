from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import unittest

import project2_run


class Project2RunTests(unittest.TestCase):
    def test_baseline_verdicts_name_the_failed_rule(self) -> None:
        baselines = project2_run.calculate_baselines()
        self.assertEqual(baselines["Equal weight"]["verdict"], "FAIL: return")
        self.assertEqual(baselines["Inverse volatility"]["verdict"], "FAIL: return")
        self.assertEqual(baselines["60/40 benchmark"]["verdict"], "FAIL: reserve")

    def test_saved_cases_and_decision_risk(self) -> None:
        all_months = project2_run.calculate_case()
        recent = project2_run.calculate_case(last_36_months=True)
        stress = project2_run.calculate_vt_stress()
        cost_stress = project2_run.calculate_cost_stress()
        self.assertEqual(
            [f"{weight:.0%}" for weight in all_months["weights"].values()],
            ["65%", "0%", "0%", "35%"],
        )
        self.assertEqual(
            [f"{weight:.0%}" for weight in recent["weights"].values()],
            ["85%", "0%", "0%", "15%"],
        )
        self.assertEqual(
            [f"{weight:.0%}" for weight in stress["weights"].values()],
            ["60%", "0%", "0%", "40%"],
        )
        self.assertEqual(
            [f"{weight:.0%}" for weight in cost_stress["weights"].values()],
            ["60%", "0%", "0%", "40%"],
        )
        self.assertEqual(f"{cost_stress['return']:.2%}", "6.74%")
        largest_change = max(
            abs(recent["weights"][ticker] - all_months["weights"][ticker])
            for ticker in all_months["weights"]
        )
        self.assertAlmostEqual(largest_change, 0.20)

    def test_infeasible_constraint_stops_the_process(self) -> None:
        self.assertIsNone(project2_run.calculate_constraint_stress())

    def test_main_exposes_baselines_stresses_and_stop(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            project2_run.main()
        rendered = output.getvalue()
        self.assertIn("Equal weight", rendered)
        self.assertIn("FAIL: return", rendered)
        self.assertIn("Annual implementation-cost stress", rendered)
        self.assertIn("STOP: no feasible portfolio", rendered)
        self.assertIn("Decision: tightly bounded pilot", rendered)


if __name__ == "__main__":
    unittest.main()
