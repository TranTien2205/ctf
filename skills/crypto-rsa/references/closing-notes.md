# Closing notes — the crypto-rsa class, the last word

## What this class is

RSA key or plaintext recovery — a challenge that hands you the numbers `n`,`e`,
`c` and asks for the plaintext or a private value. The bug is never in RSA — it
is in one of six violated preconditions: a wrap, a gap, a shared divisor, a
smooth predecessor, an exponent relation, or a leak.

## The one procedure

```
parameter-sheet → discriminator → bound-check → attack → pow-verify → record
```

The sheet names the shape; the discriminator picks the id; the bound is the
falsifier; the verify is the gate.

## The honest status

**Catalogue** — no chain card, no local solve. The corpus is published-standard
knowledge and the measured tool bounds — not verified experience. Record what
actually happens in `../field-notes.md`; a real solve here turns the class
`verified` via `tools/classify_solve.py`.

## The rules that hold

- `pow(m,e,n)==c` or `p*q==n` — the only proof.
- The bound is the falsifier — exceeded is a negative, not a retry.
- `e` large = `d` small; `e=3` ≠ automatically weak; count ≠ collision;
  balanced primes ≠ close; a public PEM = `n`,`e` only.
- The cheap attacks first; the lattice last.
- A socket that prints numbers is transport, not an oracle — a computing oracle
  is `crypto-symmetric-oracle`.

## The escalation

`tools/decide.py` owns the budget. Spent → `chain_match`, `reclassify`,
`writeup_search`, `novel_plan`, `fanout_sweep`, `solver_handoff`. A dead class
→ `knowledge/attempts/<challenge>.json` with each bound.
