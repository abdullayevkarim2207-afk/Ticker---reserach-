# Lab 17 — Point-in-Time Audit

## Decision question

**Was each number in my series knowable on the day I would have traded on it — and may Project 2 use it?**

The Streamlit app is in [`asof_app.py`](asof_app.py). From this folder, run:

```bash
python -m streamlit run asof_app.py
```

The Project 2 universe is SGOV, VGIT, BND, and VT. I use `DGS10`, the daily
10-year Treasury yield, as my chosen rate because changes in the risk-free yield
curve affect government and broad bond prices directly and also change the
discount rate applied to equities.

## Known-answer proof

These values were downloaded from ALFRED with the vintage date set to
**2026-10-05**; none is stored in the program.

| Series | Last measurement known on 2026-10-05 | Value |
|---|---:|---:|
| BAA | September 2026 | 6.47 |
| FEDFUNDS | September 2026 | 3.75 |
| DGS10 | 2026-10-02 | 5.28 |
| MORTGAGE30US | 2026-10-01 | 7.28 |

The PAYEMS probe used a vintage date of **2025-01-15**. The last measurement
then available was December 2024 at **159,536 thousand jobs**. Today's file
reports **158,316** for that same measured month. The app calculates **381**
revised values on common dates and **21** present-day values after the last date
available in that vintage. A zero revision count would have exposed an
incorrect implementation that downloaded today's file twice.

## DGS10 data card

| Field | Evidence |
|---|---|
| Source and link | Board of Governors of the Federal Reserve System, distributed by the Federal Reserve Bank of St. Louis: [FRED DGS10](https://fred.stlouisfed.org/series/DGS10) and [H.15 Selected Interest Rates](https://www.federalreserve.gov/releases/h15/) |
| Measure | Market yield on U.S. Treasury securities at 10-year constant maturity, quoted on an investment basis |
| Units | Percent per year, not seasonally adjusted |
| Frequency | Daily on business days |
| Publication lag | The H.15 is posted at 4:15 p.m. Eastern each business day. In the tested files, the latest DGS10 measurement is normally published on the next business day, so a trade before that release cannot use it. |
| Revisions | Comparing the 2026-09-30 ALFRED vintage with the 2026-10-29 FRED download produced **0 revisions on common dates**. This is evidence of no revisions in that tested window, not a promise that Treasury data can never be corrected. |
| Download date | 2026-10-29 |

### Three observations checked

| Measurement date | DGS10 value (%) | Check status |
|---|---:|---|
| 2026-10-23 | 5.00 | Personally checked against the FRED page; confirmed |
| 2026-10-26 | 5.00 | Personally checked against the FRED page; confirmed |
| 2026-10-27 | 4.99 | Personally checked against the FRED page; confirmed |

The 2026-09-30 vintage ended with the 2026-09-29 measurement at **5.26**.
Today's file still reports 5.26 for that date, with **0** common-date revisions;
today's file contains **19** later nonmissing observations. This shows the
publication lag without confusing later observations with revisions.

## How the app stops a leak

`download_today` makes one cached FRED request for a selected series.
`download_as_known` makes one cached ALFRED request with the selected vintage
date. `parse_fred_csv` treats `.` as missing, detects ALFRED's dated value-column
name, converts observations to numbers, and sorts them by measurement date.

The audit table then keeps the two concepts separate. “Values published later”
counts current observations after the vintage's final measured date, while
“Same-date values revised” compares only dates present in both files. The first
field detects publication lag; the second detects values that changed after
initial publication. Those fields stop a backtest from giving an old decision
either observations not yet released or revisions published only later.

“Cleaned the data” is not a data card because it does not identify the source,
measure, units, release lag, revision behavior, or download date. Without those
fields, another researcher cannot determine what was knowable at a decision
date or reproduce the audit.

### Student no-AI code explanation

This function downloads historical data from ALFRED based on the series and
date we choose. It first creates a URL using the series ID and vintage date,
then downloads the CSV file and cleans the data by removing missing values and
sorting everything by date. Streamlit also saves the result for one hour, so we
do not have to download the same data again. The main reason we use ALFRED
instead of FRED is to avoid look-ahead bias, since FRED might include updated
values that were not available at the time. This way, our analysis only uses
the information that was actually available on the selected date.

## Partner attack and response

**Partner's least-trusted field:** Revisions

**Partner's question, clarified for the written record:** “How do you know DGS10
was not revised later instead of the app simply failing to detect the changes?”

I compared the September 30 ALFRED vintage with the October 29 FRED file on
every overlapping date, and the app found zero changed DGS10 values. The same
comparison logic found 381 PAYEMS revisions, so the DGS10 zero is meaningful
for this tested window, although I would run the audit again before using a new
period in Project 2.

## Project 2 call

**Admit with an as-of rule.** DGS10 is a daily market rate with roughly a
one-business-day release lag and no revisions in the tested 2026-09-30 vintage,
so it may be used only from the H.15 release time at which the observation was
actually available; a decision earlier in the day must use the most recent
prior release, never today's completed history with an assumed fixed shift.

I would quarantine it again if ALFRED shows material revisions, if the H.15
release schedule changes, or if the Project 2 decision timestamp cannot be
matched to the release timestamp. It can return to admitted status only after
the lag and revision audit is rerun and the backtest rebuilds every signal from
the appropriate historical vintage.

## Reflection

DGS10 describes the prior business day's yield and is normally released in the
next business day's H.15. The app's as-known date makes the lag visible because
the newest measurement disappears when its publication was still in the
future. A backtest on today's complete file would have overstated how current
the rate signal was at the trading decision and, for revisable series such as
PAYEMS, would also have overstated the precision of the historical signal.

## Verification

Run the focused and existing checks with:

```bash
python -m unittest discover -s tests -v
```

The tests cover FRED and ALFRED column names, missing `.` values, late and
revised counts, readable unknown-series errors, monthly date labels, and all
pre-existing portfolio checks.

## AI-use disclosure

OpenAI Codex assisted with building and testing the app and organizing this
audit record. The historical values are live FRED/ALFRED downloads, not
hard-coded answers. The student personally checked the three DGS10 values on
FRED, supplied the partner-exercise confirmation, and provided the no-AI code
explanation in their own words.
