# lfsr-recover deep — reconstruct the register state

## The attack id

```bash
python3 tools/crypto_attack.py lfsr-recover --bits b0,... --width w
python3 tools/crypto_attack.py lfsr-recover --bits b0,... --taps t --width w
```

`--width` is REQUIRED. `--taps` is optional — without it, BM derives the
taps internally.

## The math

`w` consecutive output bits ARE the register state (an LFSR outputs the
shifting register's end bit). `lfsr-recover` reads the last `w` bits as
the register, and if `--taps` is omitted runs Berlekamp-Massey to get the
feedback polynomial, returning `(register, taps, width)`.

## When to use it vs `lfsr-predict`

- **`lfsr-recover`** — you have bits but NOT the taps/width confirmed; you
  want the state AND the params. Recovery.
- **`lfsr-predict`** — you have taps+width known; you want the NEXT bits.
  Prediction.

Typical chain: `berlekamp-massey` → `(w,taps)` → `lfsr-recover` → the
register → `lfsr-predict --count n` → the future keystream.

## The count floor

≥`2·width` bits if taps are unknown (BM needs `2w`); ≥`width` bits if
taps are given (the register is the last `w` bits).

## The `taps` convention

`--taps` uses **1-indexed from the LSB** — the positions counted from the
output end. A writeup indexing taps from the MSB or from 0 gives the wrong
polynomial. If `lfsr-predict` diverges, re-index the taps.

## The bit-order trap

Same as `berlekamp-massey` — a hex keystream's per-byte bit order matters.
Wrong order → the recovered register is bit-reversed → predictions fail.

## The output-shape traps

- bits not a `0/1` stream → `--keystream-hex`/`--bits-file` or normalize.
- the stream is a combiner output → not a plain LFSR → high complexity.
- gaps in the stream → the register isn't the last `w` observed bits.

## Expected signal / falsifier

- **Expected signal**: `(register, taps, width)`; `lfsr-predict` on it
  reproduces held-back bits.
- **Falsifier**: predicted bits diverge → wrong taps/width/order, or the
  stream isn't a plain LFSR.

## The verification

`lfsr-predict --count k` against `k` held-back bits. `predict == held` is
the only accept.
