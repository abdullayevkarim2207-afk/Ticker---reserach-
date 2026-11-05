"""Deterministic checks for the Lab 18 Buffett SEC skill."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


SKILL_SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / ".codex"
    / "skills"
    / "buffett-10k"
    / "scripts"
)
sys.path.insert(0, str(SKILL_SCRIPTS))

from buffett_10k import (
    analyze_companyfacts,
    audit_memo_numbers,
    compute_graham_checks,
    render_analysis,
)


DATES = [
    ("2021-08-30", "2022-08-28"),
    ("2022-08-29", "2023-09-03"),
    ("2023-09-04", "2024-09-01"),
    ("2024-09-02", "2025-08-31"),
    ("2025-09-01", "2026-08-30"),
]

COST_VALUES = {
    "RevenueFromContractWithCustomerExcludingAssessedTax": [
        226_954,
        242_290,
        254_453,
        275_235,
        303_154,
    ],
    "NetIncomeLoss": [5_844, 6_292, 7_367, 8_099, 9_226],
    "NetCashProvidedByUsedInOperatingActivities": [
        7_392,
        11_068,
        11_339,
        13_335,
        15_817,
    ],
    "PaymentsToAcquirePropertyPlantAndEquipment": [
        3_891,
        4_323,
        4_710,
        5_498,
        6_435,
    ],
    "StockholdersEquity": [20_642, 25_058, 23_622, 29_164, 35_803],
    "Liabilities": [43_515, 43_914, 46_299, 47_829, 53_346],
    "AssetsCurrent": [32_696, 35_879, 34_246, 38_861, 43_209],
    "LiabilitiesCurrent": [32_060, 33_583, 35_464, 37_733, 40_764],
}


def flow_fact(start: str, end: str, value_millions: int, filed: str) -> dict:
    return {
        "start": start,
        "end": end,
        "val": value_millions * 1_000_000,
        "form": "10-K",
        "filed": filed,
        "accn": f"test-{filed}",
    }


def instant_fact(end: str, value_millions: int, filed: str) -> dict:
    return {
        "end": end,
        "val": value_millions * 1_000_000,
        "form": "10-K",
        "filed": filed,
        "accn": f"test-{filed}",
    }


def companyfacts(
    entity: str,
    values: dict[str, list[int]],
    revenue_tag: str = "RevenueFromContractWithCustomerExcludingAssessedTax",
) -> dict:
    facts = {}
    for tag, tag_values in values.items():
        actual_tag = revenue_tag if tag == "revenue" else tag
        if actual_tag in {
            "StockholdersEquity",
            "Liabilities",
            "AssetsCurrent",
            "LiabilitiesCurrent",
        }:
            rows = [
                instant_fact(end, value, f"{2022 + index + 1}-10-10")
                for index, ((_, end), value) in enumerate(zip(DATES, tag_values))
            ]
        else:
            rows = [
                flow_fact(start, end, value, f"{2022 + index + 1}-10-10")
                for index, ((start, end), value) in enumerate(zip(DATES, tag_values))
            ]
        facts[actual_tag] = {"units": {"USD": rows}}
    return {"entityName": entity, "facts": {"us-gaap": facts}}


class BuffettLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cost_facts = companyfacts("COSTCO WHOLESALE CORP", COST_VALUES)

    def test_cost_known_answer_and_checks(self) -> None:
        analysis = analyze_companyfacts("COST", self.cost_facts)
        rows = analysis["rows"]

        self.assertEqual([row["fiscal_year_end"] for row in rows], [end for _, end in DATES])
        self.assertEqual([row["revenue"]["value"] for row in rows], COST_VALUES["RevenueFromContractWithCustomerExcludingAssessedTax"])
        self.assertEqual(
            [row["owner_earnings"]["value"] for row in rows],
            [3_501, 6_745, 6_629, 7_837, 9_382],
        )
        expected_roe = [28.3, 25.1, 31.2, 27.8, 25.8]
        self.assertEqual(
            [round(row["roe"]["value"], 1) for row in rows], expected_roe
        )
        self.assertEqual(
            analysis["checks"],
            {
                "roe_15_every_year": "pass",
                "owner_earnings_positive_every_year": "pass",
                "owner_earnings_grew": "pass",
            },
        )
        self.assertEqual(
            [round(row["current_ratio"]["value"], 2) for row in rows],
            [1.02, 1.07, 0.97, 1.03, 1.06],
        )
        self.assertEqual(
            [round(row["liabilities_to_equity"]["value"], 2) for row in rows],
            [2.11, 1.75, 1.96, 1.64, 1.49],
        )
        self.assertEqual(
            analysis["panel_checks"],
            {
                "Buffett": analysis["checks"],
                "Graham": {
                    "current_ratio_latest": "fail",
                    "net_income_positive_every_year": "pass",
                    "net_income_grew": "pass",
                },
                "Burry": {
                    "cash_flow_covers_net_income_every_year": "pass",
                    "liabilities_no_more_than_twice_equity_latest": "pass",
                },
            },
        )
        self.assertEqual(
            compute_graham_checks(rows, current_ratio_threshold=1.0)[
                "current_ratio_latest"
            ],
            "pass",
        )
        self.assertEqual(
            analysis["graham_probe_checks"]["current_ratio_latest"], "pass"
        )

    def test_latest_filing_wins_for_same_period(self) -> None:
        revenue_facts = self.cost_facts["facts"]["us-gaap"][
            "RevenueFromContractWithCustomerExcludingAssessedTax"
        ]["units"]["USD"]
        revenue_facts.append(
            flow_fact("2025-09-01", "2026-08-30", 1, "2026-01-01")
        )
        analysis = analyze_companyfacts("COST", self.cost_facts)
        self.assertEqual(analysis["rows"][-1]["revenue"]["value"], 303_154)

    def test_jpm_keeps_capex_and_owner_earnings_gaps_honest(self) -> None:
        jpm_values = {
            "revenue": [120_000, 130_000, 140_000, 150_000, 160_000],
            "NetIncomeLoss": [30_000, 32_000, 34_000, 36_000, 38_000],
            "NetCashProvidedByUsedInOperatingActivities": [
                40_000,
                41_000,
                42_000,
                43_000,
                44_000,
            ],
            "StockholdersEquity": [200_000, 205_000, 210_000, 215_000, 220_000],
        }
        analysis = analyze_companyfacts(
            "JPM", companyfacts("JPMORGAN CHASE & CO", jpm_values, "Revenues")
        )
        for row in analysis["rows"]:
            self.assertEqual(row["capital_spending"]["status"], "not found")
            self.assertEqual(row["owner_earnings"]["status"], "not found")
        self.assertEqual(
            analysis["checks"]["owner_earnings_positive_every_year"], "not known"
        )
        self.assertEqual(analysis["checks"]["owner_earnings_grew"], "not known")

    def test_unprinted_roe_is_flagged(self) -> None:
        analysis = analyze_companyfacts("COST", self.cost_facts)
        output = render_analysis(analysis)
        clean_memo = "ROE was 28.3% and the fiscal year ended 2022-08-28."
        self.assertEqual(audit_memo_numbers(clean_memo, output), [])
        self.assertEqual(
            audit_memo_numbers(clean_memo + " Hand-entered ROE was 40.0%.", output),
            ["40.0%"],
        )

    def test_all_cost_panel_memos_pass_one_number_audit(self) -> None:
        analysis = analyze_companyfacts("COST", self.cost_facts)
        repo = Path(__file__).resolve().parents[1]
        memos = [
            (repo / f"lab19_{investor}_memo_COST.md").read_text(encoding="utf-8")
            for investor in ("buffett", "graham", "burry")
        ]
        self.assertEqual(
            audit_memo_numbers("\n".join(memos), render_analysis(analysis)), []
        )


if __name__ == "__main__":
    unittest.main()
