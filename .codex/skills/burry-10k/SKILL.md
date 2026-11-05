---
name: burry-10k
description: Apply FIN 43900's Burry cash-quality and leverage checks to five years of tagged SEC 10-K facts and write an evidence-bounded memo. Use for Lab 19 Burry screening; do not use for price or valuation claims.
---

# Burry 10-K

Use the same facts, fiscal periods, tag priorities, and honest-gap rules as the
repository's `buffett-10k` skill. The shared evidence script is the only source
of numbers.

Run `scripts/burry_10k.py TICKER`. The script obtains the shared SEC analysis
and prints Burry's two coded checks: operating cash flow at least net income in
every displayed year, and latest liabilities no more than twice equity. A
missing required input makes the affected check `not known`.

Write a short memo using only numbers printed by the script. State an
`own`, `watch`, or `pass` verdict, discuss both checks, preserve every gap, and
do not add an unprinted forensic claim.

Before finishing, audit the memo with `audit_memo_numbers` from the shared
`buffett_10k.py` script. Revise until the unprinted-number list is empty.
