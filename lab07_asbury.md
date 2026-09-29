# Lab 07 — Asbury Comparable-Company Policy and Implied Range

## Before the calculation

My Ford DCF range is driven most by starting free cash flow, WACC, terminal growth, and the five explicit growth rates. In my Lab 06 sensitivity table, value falls when WACC rises and rises when terminal growth rises. The input I trust least is Ford's $3.5 billion Company adjusted free-cash-flow proxy because it excludes Ford Credit and is not a full GAAP FCFF reconciliation.

My question about peer multiples was: **How can I tell whether a difference in P/E represents mispricing or a real difference in growth, risk, business mix, or earnings quality?**

## What P/E tells me

Price-to-earnings, or P/E, is the market price of one common share divided by earnings attributable to each diluted common share. Price per share records what investors paid for one ownership unit at a specific date. Diluted EPS measures the company's GAAP profit attributable to each common share after including the possible dilution from instruments such as stock awards or convertible securities.

A 10× P/E means investors paid $10 per share for each $1 of annual diluted earnings per share. Because both inputs are per-share amounts, P/E lets me compare companies of different sizes. I can apply comparable companies' P/E multiples to the target's EPS to obtain a market-based implied share price.

This comparison adds an external market check to my DCF. The DCF depends on forecasts of cash flows, discount rates, and terminal growth, while the peer result shows how the market priced similar companies using a consistent historical earnings measure. Neither method proves fair value. A DCF may use weak forecasts, and a P/E comparison may import the market's mistakes or differences between companies.

P/E is most useful when the companies have similar business models, growth prospects, risk, accounting, fiscal periods, and earnings definitions. It becomes misleading when earnings are negative, close to zero, temporarily inflated or depressed, affected by unusual items, or based on inconsistent periods. A lower P/E does not automatically mean a better investment: the market may reasonably assign it because the company has slower expected growth, more risk, weaker earnings quality, or less durable profits.

## Case peer policy and decisions

I placed the most weight on franchised new-vehicle retail and the related used-vehicle, parts-and-service, collision, and finance-and-insurance activities. These revenue drivers and profit economics matter more than sharing a broad automotive-retail industry label. Parts and service deserves special attention because repair, warranty, maintenance, and collision work has different margins and cyclicality from vehicle sales.

| Candidate | Decision | Business evidence and reason |
|---|---|---|
| AutoNation (`AN`) | Use | AutoNation is a large U.S. franchised automotive retailer. Like Asbury, it sells new and used vehicles and earns from parts and service, collision work, and finance and insurance. Its larger scale, AutoNation USA used stores, auction and distribution operations, and captive finance company are differences to monitor, but the core dealership model is close enough for this two-peer training comparison. |
| Group 1 Automotive (`GPI`) | Qualify and use | Group 1 has the same central economics: franchised new- and used-vehicle sales, parts and service, collision repair, and finance and insurance. I qualify it because it operated in both the United States and the United Kingdom at year-end 2024, while Asbury operated in 14 U.S. states. Its geographic, currency, regulatory, and market mix can affect growth, risk, and its P/E. |

Business evidence: [Asbury 2024 Form 10-K](https://www.sec.gov/Archives/edgar/data/1144980/000114498025000077/abg-20241231.htm), [AutoNation 2024 Form 10-K](https://www.sec.gov/Archives/edgar/data/350698/000035069825000029/an-20241231.htm), and [Group 1 2024 Form 10-K](https://www.sec.gov/Archives/edgar/data/1031203/000103120325000013/gpi-20241231.htm).

## Reproduction and validation

The case is a retrospective training comparison. It pairs December 31, 2024 closing prices with FY2024 total GAAP diluted EPS reported later.

One calculation by hand:

> AutoNation P/E = $169.84 / $16.92 = 10.037825×

Run the complete calculation after opening the `Lab-07-Asbury` folder in VS Code:

```bash
python3 lab07_asbury_pe.py
```

Checked results:

| Result | Value |
|---|---:|
| AutoNation P/E | 10.037825× |
| Group 1 P/E | 11.450149× |
| Peer median P/E | 10.743987× |
| Asbury implied range | $215.81–$246.18 |
| Asbury median-implied price | $231.00 |

P/E is an equity multiple, so I multiply the peer multiple directly by Asbury's diluted EPS. I do not add cash or subtract debt.

## Changed-peer interpretation

Before running the removal test, I predicted that removing Group 1 would lower the estimate because Group 1 has the higher P/E. The output confirms that prediction: with only AutoNation remaining, the implied price is **$215.81**, a **$15.18 decrease** from the unrounded full-peer median estimate.

With one peer, there is no peer dispersion from which to form a minimum-to-maximum range. AutoNation therefore supplies a reference estimate rather than a range. This also shows that the two-peer result is sensitive to peer selection.

## Reflection

The peer comparison does not prove Asbury is fairly valued. It transfers the market's valuation of two similar but imperfect companies to Asbury's reported EPS. Differences in expected growth, brand and geographic mix, scale, risk, capital structure, unusual GAAP earnings, and earnings durability can justify different P/E multiples. I would use this result as a market cross-check alongside a DCF, while keeping the peer qualifications visible.

## AI use and educational disclaimer

This work continued from my Lab 06 Codex context. I used Codex in VS Code to help structure the standard-library Python calculation, organize the source-supported peer comparison, and check the output against the case checkpoints. I am responsible for running the file, reviewing the sources, and verifying that the calculations and explanations match my understanding.

I am not a licensed financial professional. This document is for educational purposes only and is not investment advice.

Any remaining errors are my own.
