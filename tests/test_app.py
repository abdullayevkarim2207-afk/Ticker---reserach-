from __future__ import annotations

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_FILE = Path(__file__).resolve().parents[1] / "app.py"


class Project2AppTests(unittest.TestCase):
    def test_saved_inputs_show_clear_verdicts(self) -> None:
        app = AppTest.from_file(APP_FILE, default_timeout=10).run()
        self.assertFalse(app.exception)
        self.assertIn("Mandate verdict: **PASS**", app.success[0].value)
        self.assertIn("Largest weight change: **0 points**", app.info[0].value)
        self.assertIn("PAPER PILOT ONLY", app.warning[0].value)

    def test_last_36_month_control_fails_stability_limit(self) -> None:
        app = AppTest.from_file(APP_FILE, default_timeout=10).run()
        app.toggle[0].set_value(True).run()
        self.assertFalse(app.exception)
        self.assertIn("Largest weight change: **20 points**", app.info[0].value)
        self.assertIn("**FAIL** against the 10-point limit", app.info[0].value)


if __name__ == "__main__":
    unittest.main()
