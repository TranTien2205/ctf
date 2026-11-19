# Workflow surface — the minimal procedure

## The five steps

```
inventory → discriminate → solve → verify → record
```

## The gates

```
r dup? → ecdsa-nonce-reuse
smooth? → pohlig-hellman
bounded x? → bsgs
Δ == 0? → singular_ec
#E == p? → smart_attack
k < B? → hnp-ecdsa/hnp
unvalidated P? → invalid curve
```

## The verify

`x·G == Q` or `pow(g, x, p) == h`.

## The record

`post-probe` → `../field-notes.md` → `classify_solve`/`attempts`.

## The escalate

`decide.py` — `chain_match` → `reclassify` → `writeup_search` →
`novel_plan` → `fanout_sweep` → `solver_handoff`.
