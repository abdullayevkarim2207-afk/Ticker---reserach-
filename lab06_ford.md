# Lab 06 — Ford Motor Company (F)

All dollar amounts below are USD millions except per-share amounts. The valuation perimeter is **Company excluding Ford Credit** for the starting cash-flow proxy, cash, and debt. Ford calls the starting measure “Company adjusted free cash flow,” so it is a disclosed proxy for the lab’s FCFF—not GAAP FCFF.

| Input | Value | Unit | As-of / period | SEC EDGAR locator and source | Status |
|---|---:|---|---|---|---|
| Starting FCFF | 3,500 | USD millions | FY ended Dec. 31, 2025 | Ford 2025 Form 10-K, Item 7, MD&A, “Changes in Company Cash”: Company adjusted free cash flow was $3.5bn, excluding Ford Credit. | Disclosed Company-excluding-Ford-Credit proxy for FCFF. It is not identical to the lab’s GAAP formula, so this is the input to distrust most. |
| Growth, Years 1–5 | 5%, 4%, 3%, 3%, 3% | annual FCFF growth | Forecast made Sept. 10, 2026 | Ford 2025 Form 10-K, Item 7, MD&A, “Results of Operations — 2025” and “Outlook.” | Analyst forecast: modest near-term recovery, then a fade to the long-run 3% rate. |
| WACC | 10% | annual rate | Sept. 10, 2026 | Lab estimate: 4.5% + 1.3 × 5% = 11.0% cost of equity; 6.0% × (1 − 25%) = 4.5% after-tax cost of debt; 85% equity / 15% debt gives about 10%. | Analyst estimate; not copied from the 10-K. |
| Terminal growth | 3% | perpetual annual growth | Sept. 10, 2026 | Long-run economy assumption required by the lab, not Ford-specific guidance. | Analyst assumption; below the 10% WACC. |
| Cash · debt · shares | 28,684 · 21,919 · 3,979 | USD millions · USD millions · millions of diluted shares | Dec. 31, 2025 / FY2025 | Ford 2025 Form 10-K, Item 7, “Liquidity and Capital Resources” (Company cash $28.7bn, including cash equivalents, marketable securities, and restricted cash, excluding Ford Credit); “Selected Balance Sheet Information” (current debt $5,550m and long-term debt $16,369m); Note 25, Segment Information (3,979m diluted weighted-average shares). | Sourced. Debt = 5,550 + 16,369. Company cash is $28,684m before rounding to the reported $28.7bn. |

Primary source: [Ford 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/37996/000003799626000015/f-20251231.htm), filed February 11, 2026. The filing is presented in millions except per-share data.

## Price and model readout

Ford (`F`) was **$13.90** at **13:05:18 ET on September 10, 2026** (real-time quote). Source: [Investing.com historical data](https://www.investing.com/equities/ford-motor-co-historical-data). `dcf.py` uses $13.90 as its reverse-DCF target.

Run:

```bash
python3 dcf.py
```

The terminal prints the Ford proxy valuation, its sensitivity grid, and the growth shift required to reach $13.90. Value falls as WACC rises and rises as terminal growth rises.

## Reasonableness and conditional call

Compare the base value per share with $13.90. If it is outside 0.5×–2× the market price, do not change an input merely to pull it inside. The input to distrust most is the $3.5bn FCFF proxy because it is a non-GAAP, Company-excluding-Ford-Credit measure rather than a full FCFF reconciliation.

**Watch–defer. Initiate if** Ford reports evidence that makes Company adjusted free cash flow durable and the valuation remains above $13.90 across a reasonable range of WACC and terminal growth; **otherwise defer. Monitor:** Ford Pro operating margin and warranty/recall costs next quarter.

The reverse-DCF shift is the growth assumption required to reproduce the market price while holding the other model inputs fixed. It is not proof that Ford is mispriced.
