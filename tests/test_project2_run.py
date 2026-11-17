from __future__ import annotations

import unittest

import project2_run


class Project2RunTests(unittest.TestCase):
    def test_saved_cases_and_decision_risk(self) -> None:
        all_months = project2_run.calculate_case()
        recent = project2_run.calculate_case(last_36_months=True)
        stress = project2_run.calculate_vt_stress()
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
        largest_change = max(
            abs(recent["weights"][ticker] - all_months["weights"][ticker])
            for ticker in all_months["weights"]
        )
        self.assertAlmostEqual(largest_change, 0.20)


if __name__ == "__main__":
    unittest.main()
