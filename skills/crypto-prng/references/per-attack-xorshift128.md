# Per-attack `xorshift128` — the card

## Trigger

A `xorshift128` generator (`x ^= x<<13; x ^= x>>17; x ^= x<<5`) with ≥4
consecutive 32-bit outputs.

## Command

```bash
python3 tools/crypto/xorshift128.py --outs o0,o1,o2,o3 --predict 5 --selftest
```

A standalone module — `tools/crypto/xorshift128.py`, NOT a
`crypto_attack.py` id.

## Mechanism

4 consecutive 32-bit outputs = 128 linear equations over GF(2) → recover
the 128-bit state → roll forward `--predict` outputs.

## Verify

`--predict` reproduces a held-back output.

## Falsifiers

- <4 outputs → underdetermined.
- `predict != held-back` → not xorshift128 (try xorshift64/128+ variants).

## Boundaries

- `xorshift128+`/`xorshift64*`/`xorwow` are DIFFERENT — the constants and
  state size differ; `xorshift128.py` is the specific 4×32 variant.
- `--outs` is comma-separated 32-bit ints (decimal or `0x`-prefixed).
- The state is small — the attack is exact, no lattice.
