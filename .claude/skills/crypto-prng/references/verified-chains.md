# Verified chains — the honest status

## The honest state

**No `crypto-prng` chain card exists in `knowledge/chains/` yet.** The
corpus is the standard published mechanism corpus plus the field procedure
— not locally-verified experience.

## What a real card would carry

```json
{
  "id": "prng-<slug>",
  "class": "crypto-prng",
  "signals": ["mt19937", "session_id", "getrandbits"],
  "chain": ["collect 624 outs", "mt19937-clone", "predict_next", "flag"],
  "first_confirming_probe": "crypto_attack.py mt19937-clone --outputs ...",
  "falsifier": "predict != held-back",
  "blast_radius": "read-only — offline math"
}
```

## The patterns a card captures

| Pattern | Attack |
|---|---|
| LCG, m known | `lcg-recover` |
| LCG, m unknown | `lcg-unknown-modulus` |
| LCG, truncated | `lcg-truncated` |
| LFSR bits | `berlekamp-massey`/`lfsr-*` |
| MT 624 | `mt19937-clone` |
| xorshift | `xorshift128` |
| weak seed | seed-search |

## The traps a card records

- The output shape that needed normalizing (hex/float/mod).
- The count floor that was barely met or missed.
- The convention (`--low-bits`, `--taps`) that tripped the first try.
- The seed-window bound that made the search finite.

## The promote path

Solve → `classify_solve` → `knowledge/chains/` card → `../field-notes.md`
`confirmed`. Fail → `attempts/` with the falsifier + `reopen_if`.
