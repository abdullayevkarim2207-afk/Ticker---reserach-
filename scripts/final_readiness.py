"""Audit the Project 2 freeze package without inventing human evidence."""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-submission-manifest.csv"
LEDGER = ROOT / "data" / "input-ledger.csv"

REQUIRED_FILES = (
    "README.md",
    "app.py",
    "portfolio.py",
    "project2_run.py",
    "prices.csv",
    "visible_output.md",
    "data/input-ledger.csv",
    "data/dgs10-point-in-time-signal.csv",
    "docs/data-card.md",
    "docs/decision-memo.md",
    "docs/decision-memo.pdf",
    "docs/validation-and-ai-use.md",
    "docs/validation-and-ai-use.pdf",
    "docs/draft-video-1-script.txt",
    "docs/draft-video-2-script.txt",
    "docs/draft-video-3-script.txt",
    "output/pdf/project-2-decision-memo.pdf",
    "output/pdf/project-2-validation-and-ai-use.pdf",
    "project-submission-manifest.csv",
    "requirements-docs.txt",
    "submission/WHAT-TO-SUBMIT.txt",
    "submission/COMPLETENESS-AUDIT.txt",
    "submission/REPOSITORY-LINK.txt",
    "submission/REPOSITORY-CHECKLIST.txt",
    "submission/VIDEO-1-GUIDE.txt",
    "submission/VIDEO-1-RECORDING-SCRIPT.txt",
    "submission/VIDEO-2-GUIDE.txt",
    "submission/VIDEO-2-RECORDING-SCRIPT.txt",
    "submission/VIDEO-3-GUIDE.txt",
    "submission/YOUTUBE-AND-TRANSCRIPT-LINKS.txt",
    "submission/FINAL-SUBMISSION-STATEMENT.txt",
)

DISCLOSURE_ONE = (
    "OpenAI Codex was used for code, testing, debugging, and documentation "
    "organization."
)
DISCLOSURE_TWO = (
    "The analysis and decision are mine; this is for education, not investment "
    "advice."
)
DISCLOSURE_FILES = (
    "README.md",
    "Research-Evolution.md",
    "docs/decision-memo.md",
    "docs/validation-and-ai-use.md",
    "docs/draft-video-1-script.txt",
    "docs/draft-video-2-script.txt",
    "docs/draft-video-3-script.txt",
)

MATERIAL_FACTS = {
    "65% SGOV": (
        "README.md",
        "visible_output.md",
        "docs/decision-memo.md",
        "docs/validation-and-ai-use.md",
        "docs/draft-video-1-script.txt",
        "docs/draft-video-3-script.txt",
    ),
    "85% SGOV": (
        "docs/decision-memo.md",
        "docs/validation-and-ai-use.md",
        "docs/draft-video-1-script.txt",
        "docs/draft-video-3-script.txt",
    ),
    "20-point": (
        "README.md",
        "visible_output.md",
        "docs/decision-memo.md",
        "docs/validation-and-ai-use.md",
    ),
    "paper pilot": (
        "README.md",
        "docs/decision-memo.md",
        "docs/validation-and-ai-use.md",
    ),
}

EXPECTED_LEDGER_IDS = {
    "price_history",
    "objective_return",
    "reserve_minimum",
    "reserve_eligible_assets",
    "allocation_grid",
    "expected_return_method",
    "volatility_method",
    "benchmark",
    "stability_limit",
    "window_stress",
    "vt_estimate_stress",
    "cost_stress",
    "constraint_stress",
    "dgs10_signal",
    "dgs10_watch_threshold",
    "pilot_size",
    "pilot_duration",
}


def read_text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def audit_files() -> list[str]:
    return [f"missing required file: {name}" for name in REQUIRED_FILES if not (ROOT / name).is_file()]


def audit_disclosures() -> list[str]:
    errors = []
    for name in DISCLOSURE_FILES:
        text = read_text(name)
        opening = "\n".join(text.splitlines()[:12])
        if DISCLOSURE_ONE not in opening or DISCLOSURE_TWO not in opening:
            errors.append(f"required opening disclosure missing or too late: {name}")
    return errors


def audit_material_facts() -> list[str]:
    errors = []
    for fact, files in MATERIAL_FACTS.items():
        for name in files:
            if fact.lower() not in read_text(name).lower():
                errors.append(f"material fact {fact!r} missing from {name}")
    return errors


def audit_ledger() -> list[str]:
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    ids = {row["input_id"] for row in rows}
    errors = [f"input ledger missing row: {item}" for item in sorted(EXPECTED_LEDGER_IDS - ids)]
    for row in rows:
        for field in ("value", "units", "as_of_or_period", "definition", "source", "transformation", "decision_use", "status"):
            if not row.get(field, "").strip():
                errors.append(f"input ledger {row.get('input_id', '<unknown>')} has blank {field}")
    return errors


def audit_manifest() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    blockers: list[str] = []
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 12:
        errors.append(f"manifest has {len(rows)} rows; expected 12")
    for row in rows:
        if row.get("required", "").lower() != "yes":
            continue
        unresolved_fields = [
            field
            for field, value in row.items()
            if "UNRESOLVED" in (value or "").upper()
        ]
        if unresolved_fields:
            blockers.append(
                f"{row.get('item', '<unknown>')}: unresolved {', '.join(unresolved_fields)}"
            )
        limits = {"Video 1": 180, "Video 2": 300, "Video 3": 300}
        item = row.get("item", "")
        duration = row.get("duration_or_as_of", "")
        match = re.fullmatch(r"(\d+):(\d{2})", duration)
        if item in limits and match:
            seconds = int(match.group(1)) * 60 + int(match.group(2))
            if seconds > limits[item]:
                blockers.append(
                    f"{item}: duration {duration} exceeds {limits[item] // 60}:00 maximum"
                )
    return errors, blockers


def audit_runner() -> list[str]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "project2_run.py")],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    errors = []
    if result.returncode != 0:
        return [f"project2_run.py exited {result.returncode}: {result.stderr.strip()}"]
    for expected in (
        "Equal weight",
        "FAIL: return",
        "SGOV 65% / VGIT 0% / BND 0% / VT 35%",
        "SGOV 85% / VGIT 0% / BND 0% / VT 15%",
        "Annual implementation-cost stress (25 basis points)",
        "STOP: no feasible portfolio exists",
        "Decision: tightly bounded pilot",
    ):
        if expected not in result.stdout:
            errors.append(f"runner output missing: {expected}")
    return errors


def audit_duplicates() -> list[str]:
    errors = []
    pointer = read_text("decision_memo.md")
    if "Superseded pointer" not in pointer or "docs/decision-memo.md" not in pointer:
        errors.append("root decision_memo.md is not a clear pointer to the canonical memo")
    if (ROOT / "project-submission-manifest-template.csv").read_bytes() != MANIFEST.read_bytes():
        errors.append("manifest template copy differs from canonical manifest")
    return errors


def audit_locked_record() -> list[str]:
    """Verify that the claimed prediction really predates the result commit."""
    errors = []
    prediction_commit = "9ec9d32"
    result_commit = "dbf17bb"
    prediction = subprocess.run(
        ["git", "show", f"{prediction_commit}:LAB20_READINESS.md"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if prediction.returncode != 0:
        errors.append(f"locked prediction commit is unavailable: {prediction_commit}")
    else:
        for expected in (
            "**Old value:** 6.50% annually",
            "**New value:** 6.80% annually",
            "VT allocation will increase from 35% to around 40%",
            "recommendation to stay as a paper\npilot",
        ):
            if expected not in prediction.stdout:
                errors.append(
                    f"locked prediction commit {prediction_commit} is missing: {expected}"
                )

    result = subprocess.run(
        ["git", "show", f"{result_commit}:LAB20_READINESS.md"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        errors.append(f"changed-input result commit is unavailable: {result_commit}")
    else:
        for expected in (
            "SGOV 60%, VGIT 0%, BND 0%, VT 40%",
            "**Committee decision:** PAPER PILOT ONLY",
        ):
            if expected not in result.stdout:
                errors.append(
                    f"changed-input result commit {result_commit} is missing: {expected}"
                )

    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", prediction_commit, result_commit],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if ancestry.returncode != 0:
        errors.append("locked prediction commit does not precede the result commit")
    return errors


def audit() -> tuple[list[str], list[str], list[str]]:
    errors = []
    errors.extend(audit_files())
    errors.extend(audit_disclosures())
    errors.extend(audit_material_facts())
    errors.extend(audit_ledger())
    manifest_errors, blockers = audit_manifest()
    errors.extend(manifest_errors)
    errors.extend(audit_runner())
    errors.extend(audit_duplicates())
    errors.extend(audit_locked_record())

    warnings = []
    approval = read_text("docs/student-final-steps.md")
    if "PENDING - I reviewed" in approval:
        blockers.append("student approval statement remains pending")
    if not (ROOT / "docs" / "edition-a.pdf").is_file():
        warnings.append(
            "Edition A is unavailable; Research Evolution truthfully discloses the missing baseline"
        )
    for number in (1, 2, 3):
        if not (ROOT / "docs" / f"transcript-video-{number}.txt").is_file():
            blockers.append(f"corrected transcript for Video {number} is missing")
    if "LOGIN REQUIRED" in MANIFEST.read_text(encoding="utf-8"):
        warnings.append("optional Streamlit deployment is not publicly accessible")
    return errors, blockers, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return a failure code when human-completion blockers remain",
    )
    args = parser.parse_args()
    errors, blockers, warnings = audit()
    print("PROJECT 2 FINAL READINESS")
    print(f"Mechanical errors: {len(errors)}")
    for item in errors:
        print(f"  ERROR: {item}")
    print(f"Human-completion blockers: {len(blockers)}")
    for item in blockers:
        print(f"  TODO: {item}")
    print(f"Warnings: {len(warnings)}")
    for item in warnings:
        print(f"  WARNING: {item}")
    if errors:
        return 1
    if args.strict and blockers:
        return 2
    print("Mechanical package checks pass; do not submit until human blockers are cleared.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
