# Per-family LFSR — the linear-feedback branch

## The three attacks

| Attack | Trigger | Card |
|---|---|---|
| `berlekamp-massey` | taps unknown, ≥2·w bits | `per-attack-berlekamp-massey.md` |
| `lfsr-recover` | state/taps reconstruct | `per-attack-lfsr-recover.md` |
| `lfsr-predict` | taps+width known, roll forward | `per-attack-lfsr-predict.md` |

## The discriminator

```
taps known?   → lfsr-predict (--taps --width --count)
taps unknown? → berlekamp-massey → lfsr-recover → lfsr-predict
```

## The invariants

- `--bits` is explicit `0,1,0,...` OR `--keystream-hex` packed bits OR
  `--bits-file`.
- `--taps` is the module's **1-indexed-from-LSB** convention.
- `--width` is the register width `w`; `--count` the next-bits to emit.
- ≥2·w bits to pin the recurrence.

## The chain

```
keystream → berlekamp-massey → (width, taps)
          → lfsr-recover → register state
          → lfsr-predict --count n → next bits
```

## The verify

Reproduce a held-back bit window — never "the taps look plausible".

## The boundary

A nonlinear combiner/filter on top of an LFSR → BM returns a huge linear
complexity → not a raw LFSR — different problem.
