# Per-attack `lfsr-predict` — the card

## Trigger

LFSR with taps + width KNOWN and a keystream segment — roll the register
forward `--count` bits.

## Command

```bash
python3 tools/crypto_attack.py lfsr-predict \
  --bits b0,b1,... --taps t --width w --count n
```

## Mechanism

`lfsr.lfsr_predict` — apply the recurrence forward `n` steps.

## Verify

The `n` predicted bits match the actual next `n` keystream bits.

## Falsifiers

- `taps`/`width` wrong → predictions diverge at bit `w`.
- keystream segment not aligned to the register → shift it.

## Boundaries

- `--taps` convention is `1`-indexed-from-LSB (the module's own) — a tap
  list in a different convention predicts garbage.
- `--count` is how many NEXT bits to emit — not the total.
- `lfsr-recover`/`berlekamp-massey` supply the taps/width this needs.
