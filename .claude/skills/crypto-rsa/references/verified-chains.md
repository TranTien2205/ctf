# Verified chains — honest status

## Standing: CATALOGUE

No `crypto-rsa` challenge has been solved and filed in `knowledge/chains/` yet.
Nothing in this skill is verified local experience — it is published-standard
cryptanalytic knowledge plus the measured `tools/crypto_attack.py` attack
bounds.

## The evidence level

`bug-classes.json` carries `crypto-rsa` at evidence level **catalogue** — a real,
standard class that nothing in this toolkit has solved. Never present a
catalogue technique as local experience; never claim one worked here.

## What a solve produces

When a real `crypto-rsa` challenge is solved:

```bash
python3 tools/classify_solve.py --chain <new-chain-id>
```

files the chain card into `knowledge/chains/` and may raise the class to
`verified`. The chain card carries:
- `id`, `bug_class: crypto-rsa`, `confidence`, `evidence_level`
- `signals` — the fingerprints that fired (`e≈n`, `n count ≥2`, `next_prime`)
- `first_confirming_probe` — the `crypto_attack.py` call that fired
- `mechanism` — the violated precondition
- `verify` — `pow(m,e,n)==c` / `p*q==n`
- `blast_radius`, `related_chain_ids`, `novel_vs_variant`

## The honest gap

The attack list, bounds, and procedures are published-standard (Wiener,
Boneh-Durfee, Coppersmith, Håstad, Fermat, Pollard, Bellcore, Franklin-Reiter)
— none has produced a flag here. `../field-notes.md` records what actually happens
on the first real RSA challenge; `negative-results.md` and
`knowledge/attempts/` record what did not work.

## The chain cards today

`knowledge/chains/` holds 73 cards — none is a `crypto-rsa` card. The web
classes dominate; crypto has no verified chain yet.
