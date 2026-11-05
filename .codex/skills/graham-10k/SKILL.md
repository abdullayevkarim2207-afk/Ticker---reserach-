---
name: graham-10k
description: Apply FIN 43900's Graham liquidity and earnings checks to five years of tagged SEC 10-K facts and write an evidence-bounded memo. Use for Lab 19 Graham screening; do not use for price or valuation claims.
---

# Graham 10-K

Use the same facts, fiscal periods, tag priorities, and honest-gap rules as the
repository's `buffett-10k` skill. The shared evidence script is the only source
of numbers.

Run `scripts/graham_10k.py TICKER`. The script obtains the shared SEC analysis
and prints Graham's three coded checks: latest current ratio at least 2.0, net
income positive every year, and net income growth from the first displayed year
to the last. A missing required input makes the affected check `not known`.

Write a short memo using only numbers printed by the script. State an
`own`, `watch`, or `pass` verdict, discuss all three checks, and preserve every
gap. Keep the 2.0 threshold in the final screen. The 1.0 setting is only the Lab
19 threshold probe; record that its result can differ without treating it as the
kept rule.

Before finishing, audit the memo with `audit_memo_numbers` from the shared
`buffett_10k.py` script. Revise until the unprinted-number list is empty.
