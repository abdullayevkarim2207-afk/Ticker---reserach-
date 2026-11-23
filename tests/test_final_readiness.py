from __future__ import annotations

import unittest

from scripts import final_readiness


class FinalReadinessTests(unittest.TestCase):
    def test_mechanical_package_is_consistent(self) -> None:
        errors, blockers, warnings = final_readiness.audit()
        self.assertEqual(errors, [])
        self.assertTrue(
            any("Edition A is unavailable" in item for item in warnings)
        )
        self.assertTrue(any("Video 1" in item for item in blockers))
        self.assertIn(
            "optional Streamlit deployment is not publicly accessible", warnings
        )


if __name__ == "__main__":
    unittest.main()
