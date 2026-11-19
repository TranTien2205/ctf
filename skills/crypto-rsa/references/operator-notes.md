# Operator notes — the RSA engagement, in practice

## The first ten minutes

- Parse every `n`,`e`,`c`; note the bit-lengths.
- Read the keygen — `next_prime`, `getPrime(d)`, `seed`, `p-1`, `e=3`, no pad.
- A PEM is `n`,`e` — extract and move on.
- `crypto_attack.py list` — the inventory.

## The next twenty

- The discriminator picks the attack — don't pick a favourite.
- Cheap first: fermat, batch-gcd, small-e, common-modulus, pollard, wiener.
- The bound is the falsifier — read the applicability line.

## The verify

`pow(m,e,n)==c` or `p*q==n`. A plausible flag that fails `pow` is a decoy.

## The honest status

Catalogue — no local solve. The corpus is published-standard; the bounds are
measured; nothing is verified experience. Record what happens in `../field-notes.md`.

## The stall points

- The lattice is slow → check `lll_backend`; a bound exceeded is a falsifier.
- `inverse` fails → `gcd(e,φ)>1` → `eth-root`.
- batch-gcd empty → all `gcd=1` → negative.
- `pow` fails → decoy / wrong root / a pad.
- Nothing fires → re-read the source; else reclassify.

## The discipline

Five probes spent in one attack family with no new signal → change the
discriminator row. A bound exceeded → record the negative. `tools/decide.py`
owns the budget; escalate via `chain_match`, `reclassify`, `writeup_search`,
`novel_plan`, `fanout_sweep`, `solver_handoff`.
