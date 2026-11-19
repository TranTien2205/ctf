# per-attack lfsr-recover deep — the register reconstruction

## The command

```bash
python3 tools/crypto_attack.py lfsr-recover --bits b0,... --width w
python3 tools/crypto_attack.py lfsr-recover --bits b0,... --taps t --width w
```

`--width` required; `--taps` optional (BM-derived if omitted).

## The math

`w` consecutive output bits ARE the register — an LFSR emits the register's
end bit each clock. `lfsr-recover` reads the last `w` observed bits as the
register and, if `--taps` is omitted, runs BM to derive the feedback
polynomial. Returns `(register, taps, width)`.

## The position in the chain

`lfsr-recover` is the middle — it takes a bitstream and yields the
register + params, which `lfsr-predict` then rolls forward:

```
berlekamp-massey → (w,taps) → lfsr-recover → register → lfsr-predict --count
```

## The count floor

- ≥`2·width` bits if taps unknown (BM needs `2w`).
- ≥`width` bits if `--taps` given (the register is the last `w` bits).

## The `--taps` convention

1-indexed from the LSB (output end). A degree-`d` polynomial tap in a
writeup maps to position `w-d` — the wrong convention mirrors the
polynomial → `predict` diverges.

## The bit-order trap

`--bits` = comma `0,1,...`; `--keystream-hex`/`--bits-file` unpack bytes.
The per-byte bit ORDER (MSB-first vs LSB-first) changes the stream — a
wrong order mirrors the register → predictions fail. Flip the order.

## The Fibonacci-vs-Galois nuance

- **Fibonacci**: the XOR'd taps feed the new bit; output = end bit. What
  the tools model.
- **Galois**: the XOR applies to the register after shifting; output =
  end bit. A different but equivalent recurrence — BM still works on the
  output bits; the `taps` convention differs.

## The combiner falsifier

A nonlinear combiner output isn't a plain LFSR — `lfsr-recover`'s BM gives
`L ≈ n/2` → the falsifier → correlation attack.

## Expected signal / falsifier

- **Expected**: `(register, taps, width)`; `lfsr-predict` reproduces
  held-back bits.
- **Falsifier**: `L ≈ n/2` / predicted diverges → not a plain LFSR /
  wrong convention.
