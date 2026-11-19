# Onboarding deep — the class in 15 minutes

## The mental model

Every attack here recovers a scalar from a leak. The leaks:

- **Same `k` twice** — ECDSA's fatal reuse.
- **Small `k`** — the lattice turns bounded `k_i` into `d`.
- **Partial `k`** — same lattice, fewer sigs→more.
- **Smooth order** — `ord` factors → dlog is easy.
- **Bounded `x`** — `√B` search.
- **Broken curve** — anomalous/singular/invalid — the group isn't a group.

## The tool map

```
crypto_attack.py
├── ecdsa-nonce-reuse  --sigs --order          (hnp.ecdsa_recover_nonce_reuse)
├── hnp-ecdsa          --sigs --order --nonce-* (hnp.ecdsa_recover_biased_nonce)
├── hnp                --t --u --modulus --bound (hnp.hnp_solve)
├── pohlig-hellman     --g --h --p --order      (dlog.pohlig_hellman)
├── bsgs               --g --h --p --order      (dlog.bsgs)
├── smoothness         --n                      (numtheory.smoothness)
├── list / list --json / describe <id>
└── selftest
tools/crypto/
├── ec.py              curve arithmetic
├── smart_attack.py    #E == p solver
├── singular_ec.py     Δ == 0 solver
├── dlog.py            PH + BSGS
├── hnp.py             lattice + reuse/biased + required_signatures
├── lll.py             pure-python LLL
└── numtheory.py       smoothness, CRT, gcd
```

## The verify reflex

`x·G == Q` or `pow(g, x, p) == h` — the only proof. A scalar that doesn't
reproduce the public key is a wrong input, not a near-miss.

## The record reflex

`post-probe` evidence ⊆ response → `../field-notes.md` → `classify_solve.py`
/ `knowledge/attempts/` → `decide.py` rungs on stuck.

## The catalogue caveat

Nothing solved here yet — the corpus is the field procedure; the first
solve writes the first confirmed field note.
