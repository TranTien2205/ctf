# Workflow variant — the phases as a decision tree

```
                 ┌─ collect outputs (consecutive, raw)
                 ▼
           fingerprint the generator
                 │
   ┌─────┬───────┼───────┬────────┐
   LCG   LFSR    MT    xorshift  seed
   │      │       │       │        │
 m known? taps?  624?    4?     bounded?
   │      │       │       │        │
 recover BM→   clone   invert  enumerate
   │   recover  │       │        │
   │   predict  │       │        │
   └──────┴───────┴───────┴────────┘
                 ▼
          predict == held-back?
            yes → use → flag
            no  → falsifier → attempts → decide.py
```

## Phase details

### collect

- consecutive = no gaps in stream index
- raw = ints, not hex/float/mod/randint
- enough = the count floor for the chosen attack

### fingerprint

- name in source → family
- gcd/BM/clone → structure → family
- `urandom`/`secrets` → OUT

### route

- LCG: `m`? → recover; `m`? → unknown-modulus; `a,c,m`+`x>>b` → truncated
- LFSR: taps? → predict; else → BM → recover
- MT: 624 → clone
- xorshift: 4 → invert
- seed: bounded window → enumerate

### solve

- the matching `crypto_attack.py <id>` or `xorshift128.py`

### verify

- `predict == held-back` — the only accept

### close

- use → flag → post-probe/pre-flag → record
- falsify → attempts + reopen_if → decide.py rung
