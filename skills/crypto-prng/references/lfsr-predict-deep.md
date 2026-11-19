# lfsr-predict deep — roll the register forward

## The attack id

```bash
python3 tools/crypto_attack.py lfsr-predict \
  --bits b0,... --taps t --width w --count n
```

`--taps` and `--width` are REQUIRED. `--count n` = how many next bits to
emit.

## The math

With taps `t` and width `w` known, the recurrence is fixed. The last `w`
observed bits are the register; each step outputs the register's end bit
and shifts in the XOR of the tap bits. Roll it `--count` steps → the next
`--count` output bits.

## The chain position

`lfsr-predict` is the CLOSE of the LFSR chain, not the opener:

```
bits → berlekamp-massey → (w, taps)     # if taps unknown
     → lfsr-recover → register
     → lfsr-predict --count n → the future keystream
     → ct ⊕ keystream → flag
```

If taps+width are already known (in source or a writeup), skip BM/recover
and run `lfsr-predict` directly.

## The required flags

- `--taps` — the feedback positions, **1-indexed from the LSB**. The tool
  does NOT accept `--taps` omitted here (unlike `lfsr-recover`).
- `--width` — the register width `w`.
- `--count` — how many future bits; match it to the flag length you need.

## The convention traps — the two most common failures

1. **`--taps` indexing** — 1-indexed from the LSB (the output end). A
   writeup using MSB-index or 0-index gives a mirrored/shifted polynomial.
   `predict` diverges → re-index.
2. **bit order** — the input `--bits`/`--keystream-hex` stream's bit order
   per byte. Wrong order → the register is mirrored → predictions fail.

## The count

`--count n` — emit `n` bits. For a flag of `L` bytes, `--count = 8·L` at
minimum (plus a few to verify). Over-count is free; under-count truncates
the flag.

## The failure modes

- `predict != held-back` → taps/width/order wrong, or the stream isn't a
  plain LFSR (combiner — high BM complexity).
- output is all-zeros or fixed → the register hit a degenerate state →
  wrong width.

## The stream-cipher close

`flag_ct ⊕ predicted_keystream = flag`. The predicted bits ARE the
keystream; XOR against the ciphertext bytes.

## Expected signal / falsifier

- **Expected signal**: the next `n` bits, matching held-back bits.
- **Falsifier**: predicted bits diverge → wrong taps/width/order/variant.
