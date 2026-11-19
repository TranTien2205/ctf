# per-attack lfsr-predict deep — the forward roll

## The command

```bash
python3 tools/crypto_attack.py lfsr-predict \
  --bits b0,... --taps t --width w --count n
```

`--taps` and `--width` REQUIRED; `--count` = the next `n` bits.

## The math

Taps `t` + width `w` fix the recurrence. The last `w` observed bits are
the register; roll it `--count` steps → the next `--count` output bits.

## The chain close

`lfsr-predict` is the LAST step, not the first — it consumes the
`(taps, width)` that `berlekamp-massey`/`lfsr-recover` produced:

```
bits → BM → (w,taps) → lfsr-recover → register → lfsr-predict --count n
→ the future keystream → ct ⊕ ks → flag
```

If taps+width are already known (in source/writeup), skip recovery and
run `lfsr-predict` directly.

## The `--count` sizing

`--count n` emits `n` bits. For a flag of `L` bytes → `8·L` bits minimum
(plus a few to verify). Over-count is free.

## The two conventions — the two most common failures

1. **`--taps` indexing** — 1-indexed-LSB. A writeup's `x^16+x^14+x^13+
   x^11+1` indexed by degree maps to positions `w-d` — the mirrored
   polynomial → `predict` diverges.
2. **bit order** — the `--bits`/`--keystream-hex` stream's per-byte order.
   Wrong order → mirrored register → `predict` diverges.

## The failure modes

- `predict != held` → taps/width/order wrong, or the stream isn't a plain
  LFSR.
- all-zeros output → the register hit a degenerate (zero) state → wrong
  width/order.
- taps don't match the width → `width` is the register size; taps must be
  `≤ width`.

## The stream-cipher close

`ct ⊕ predicted_keystream = flag` — the predicted bits ARE the keystream.

## Expected signal / falsifier

- **Expected**: `predict == held` bits.
- **Falsifier**: predicted diverges → wrong taps/width/order, or not a
  plain LFSR (combiner).
