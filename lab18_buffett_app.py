"""Streamlit interface for the FIN 43900 Lab 18 Buffett 10-K skill."""

from __future__ import annotations

import os
from pathlib import Path
import sys

import pandas as pd
import streamlit as st


REPO_ROOT = Path(__file__).resolve().parent
SKILL_SCRIPTS = REPO_ROOT / ".codex" / "skills" / "buffett-10k" / "scripts"
if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))

from buffett_10k import (  # noqa: E402
    CHECK_LABELS,
    EdgarError,
    METRIC_LABELS,
    analyze_ticker,
    audit_memo_numbers,
    format_cell,
    render_analysis,
    validate_user_agent,
)


DECISIONS = {
    "COST": (
        "I trust the COST verdict as a consistent screen because all three checks "
        "are reproduced from tagged 10-K facts, but it is not a complete investment decision."
    ),
    "JPM": (
        "I do not trust an owner-earnings verdict on JPM because the required capital-spending "
        "fact is not found, so both owner-earnings checks remain not known."
    ),
}


@st.cache_data(show_spinner=False, ttl=3600)
def download_analysis(ticker: str, user_agent: str) -> dict:
    """Cache public SEC facts for one hour to avoid repeated requests."""
    return analyze_ticker(ticker, user_agent)


def display_table(analysis: dict) -> pd.DataFrame:
    """Build the visible tagged table without recomputing any values."""
    records = []
    metric_order = (
        "revenue",
        "net_income",
        "operating_cash_flow",
        "capital_spending",
        "equity",
        "roe",
        "owner_earnings",
    )
    for row in analysis["rows"]:
        record = {"Fiscal year end": row["fiscal_year_end"]}
        for metric in metric_order:
            record[METRIC_LABELS[metric]] = format_cell(row[metric], metric)
        records.append(record)
    return pd.DataFrame.from_records(records)


def chart_frame(analysis: dict) -> pd.DataFrame:
    """Return only printed owner earnings and net income for charting."""
    records = []
    for row in analysis["rows"]:
        owner = row["owner_earnings"]
        net_income = row["net_income"]
        records.append(
            {
                "Fiscal year end": row["fiscal_year_end"],
                "Owner earnings": owner["value"] if owner["status"] == "ok" else None,
                "Net income": net_income["value"] if net_income["status"] == "ok" else None,
            }
        )
    return pd.DataFrame.from_records(records)


def load_memo(ticker: str) -> str:
    path = REPO_ROOT / f"lab18_buffett_memo_{ticker}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return (
        f"# Buffett-style memo — {ticker}\n\n"
        "No saved memo was found. Run the `buffett-10k` skill for this ticker, "
        "then save its evidence-bounded memo in the repository root.\n"
    )


def main() -> None:
    st.set_page_config(page_title="Lab 18 · Buffett 10-K", page_icon="📚", layout="wide")
    st.title("Lab 18 · Buffett 10-K Skill")
    st.caption(
        "Data from SEC EDGAR; built with AI help, a learning demonstration, "
        "not investment advice."
    )

    with st.sidebar:
        st.header("Run the skill")
        ticker = st.text_input("Ticker", value="COST").strip().upper()
        environment_agent = os.environ.get("SEC_USER_AGENT", "")
        if environment_agent:
            st.success("Using SEC_USER_AGENT from this session.")
            user_agent = environment_agent
        else:
            user_agent = st.text_input(
                "SEC User-Agent (name and email)",
                type="password",
                help="Sent to the SEC for this session and never written to the repository.",
            )
        run = st.button("Analyze 10-K facts", type="primary", use_container_width=True)

    if not run and "analysis" not in st.session_state:
        st.info("Enter the SEC User-Agent requested for automated access, then analyze COST.")
        return

    if run:
        try:
            declared_agent = validate_user_agent(user_agent)
            with st.spinner("Downloading keyless SEC EDGAR company facts…"):
                st.session_state.analysis = download_analysis(ticker, declared_agent)
        except EdgarError as exc:
            st.error(str(exc))
            return

    analysis = st.session_state.analysis
    ticker = analysis["ticker"]
    st.subheader(f"{ticker} · {analysis['company']}")

    chart = chart_frame(analysis)
    if chart[["Owner earnings", "Net income"]].notna().any().any():
        st.line_chart(
            chart,
            x="Fiscal year end",
            y=["Owner earnings", "Net income"],
            y_label="USD millions",
        )
    else:
        st.warning("Owner earnings and net income are not found for the displayed years.")

    st.subheader("Five fiscal years · values and XBRL tags")
    st.dataframe(display_table(analysis), hide_index=True, use_container_width=True)

    st.subheader("Buffett checks · computed in code")
    check_columns = st.columns(3)
    for column, (key, label) in zip(check_columns, CHECK_LABELS.items()):
        column.metric(label, analysis["checks"][key].upper())

    st.subheader("Evidence-bounded memo")
    memo = st.text_area(
        "Edit the memo to run the number-origin probe",
        value=load_memo(ticker),
        height=360,
        key=f"memo_{ticker}",
    )
    flagged = audit_memo_numbers(memo, render_analysis(analysis))
    if flagged:
        st.error("Numbers not printed by the script: " + ", ".join(f"`{item}`" for item in flagged))
    else:
        st.success("Number audit passed: every numeric claim appears in the script output.")

    st.markdown("**Trust decision:** " + DECISIONS.get(ticker, "Not recorded for this ticker."))

    with st.expander("Exact script output used by the number audit"):
        st.code(render_analysis(analysis), language="text")


if __name__ == "__main__":
    main()
