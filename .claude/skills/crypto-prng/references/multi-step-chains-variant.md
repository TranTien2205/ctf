# Multi-step chains variant — the solve sequences, compact

## Chain shapes

```
oracle → collect → fingerprint → attack → verify → use → flag
```

## The chains

- **LCG**: outs → gcd → `lcg-recover`/`lcg-unknown-modulus` → predict →
  forge → flag.
- **LFSR**: `flag{` prefix → keystream → BM → `lfsr-predict` → `ct⊕ks` →
  flag.
- **MT**: 624 words → `mt19937-clone` → predict → hijack → flag.
- **xorshift**: 4 words → `xorshift128` → predict → flag.
- **seed**: `iat` bound → enumerate → match → predict → flag.
- **truncated**: `x>>b` + `a,c,m` → `lcg-truncated --low-bits` → state →
  key → flag.

## The chain-choice rule

- ≥624 raw words → MT.
- bitstream + known-plaintext → LFSR.
- `a,c,m` known + `x>>b` → truncated LCG.
- mod-m ints → LCG.
- small seed → seed-search.
- 4 words → xorshift.

## The handoff

Verify fails → troubleshoot → falsifier → attempts → `decide.py` rung.
