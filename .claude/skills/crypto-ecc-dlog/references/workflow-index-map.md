# Workflow index map — the procedures → files → commands, the map edition

## The map

```
read      → detection*.md              → parse
gate      → per-check*/per-boundary*   → smoothness/Δ/#E/count
route     → per-family-*/per-attack-*  → pick attack
solve     → payload-dictionary*/deep   → crypto_attack.py
verify    → verify*/per-check*         → E.mul/pow
record    → field-notes/evidence       → post-probe
escalate  → falsifiers*/decide.py      → rung
```

## The command anchors

| Phase | Command |
|---|---|
| gate | `Counter(r)` · `smoothness --n ord` · `Δ` · `#E` |
| solve | `ecdsa-nonce-reuse`/`hnp-ecdsa`/`hnp`/`pohlig-hellman`/`bsgs`/`smart_attack`/`singular_ec` |
| verify | `E.mul(G,d) == Q` · `pow(g,x,p) == h` |
| record | `post-probe` · `classify_solve` |
| escalate | `decide.py` |

## The branch maps

- nonce branch → `per-family-nonce*.md`.
- dlog branch → `per-family-dlog*.md`.
- defect branch → `per-family-curve-defect*.md`.
