from __future__ import annotations

import unittest

import pandas as pd

import asof_app


class AsofAppTests(unittest.TestCase):
    def test_parses_fred_and_alfred_column_names_and_drops_missing(self) -> None:
        fred = "observation_date,DGS10\n2026-10-01,5.24\n2026-10-02,.\n"
        alfred = "observation_date,DGS10_20261005\n2026-10-01,5.24\n2026-10-02,5.28\n"
        fred_values = asof_app.parse_fred_csv(fred, "DGS10")
        alfred_values = asof_app.parse_fred_csv(alfred, "DGS10")
        self.assertEqual(len(fred_values), 1)
        self.assertEqual(float(alfred_values.iloc[-1]), 5.28)

    def test_counts_late_values_and_same_date_revisions(self) -> None:
        vintage = pd.Series(
            [100.0, 101.0],
            index=pd.to_datetime(["2024-11-01", "2024-12-01"]),
        )
        today = pd.Series(
            [100.0, 99.0, 102.0, 103.0],
            index=pd.to_datetime(
                ["2024-11-01", "2024-12-01", "2025-01-01", "2025-02-01"]
            ),
        )
        self.assertEqual(asof_app.audit_counts(today, vintage), (2, 1))

    def test_unknown_or_empty_download_has_readable_error(self) -> None:
        with self.assertRaisesRegex(asof_app.SeriesDownloadError, "No numeric"):
            asof_app.parse_fred_csv(
                "observation_date,UNKNOWN\n2026-01-01,.\n", "UNKNOWN"
            )

    def test_monthly_dates_are_displayed_as_month_and_year(self) -> None:
        values = pd.Series(
            [1.0, 2.0, 3.0],
            index=pd.to_datetime(["2026-07-01", "2026-08-01", "2026-09-01"]),
        )
        self.assertEqual(
            asof_app.format_measured_date(values.index[-1], values),
            "September 2026",
        )

    def test_latest_move_and_market_strip_use_each_loaded_series(self) -> None:
        values = pd.Series(
            [4.90, 4.99],
            index=pd.to_datetime(["2026-10-26", "2026-10-27"]),
            name="DGS10",
        )
        latest, change = asof_app.latest_move(values)
        self.assertEqual(latest, 4.99)
        self.assertAlmostEqual(change, 0.09)
        strip = asof_app.market_strip_html({"DGS10": {"today": values}})
        self.assertIn("DGS10", strip)
        self.assertIn("4.99", strip)
        self.assertIn("move-up", strip)

    def test_normalize_to_100_handles_different_scales(self) -> None:
        frame = pd.DataFrame(
            {"RATE": [5.0, 5.5], "JOBS": [100_000.0, 101_000.0]},
            index=pd.to_datetime(["2026-01-01", "2026-02-01"]),
        )
        normalized = asof_app.normalize_to_100(frame)
        self.assertEqual(normalized.iloc[0].tolist(), [100.0, 100.0])
        self.assertEqual(normalized.iloc[1].round(2).tolist(), [110.0, 101.0])


if __name__ == "__main__":
    unittest.main()
