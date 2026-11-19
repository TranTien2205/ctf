# Per-attack `lfsr-recover` — the card

## Trigger

An LFSR keystream where the register STATE (and possibly taps) must be
reconstructed — taps unknown or partially known.

## Command

```bash
python3 tools/crypto_attack.py lfsr-recover \
  --bits b0,b1,... --width w
# or with taps if partial knowledge:
python3 tools/crypto_attack.py lfsr-recover \
  --bits b0,b1,... --taps t --width w
```

## Mechanism

`lfsr.lfsr_reconstruct` — linear solve over GF(2) for the register state
(and taps if `--taps` not given).

## Verify

Roll forward → the next `w` keystream bits reproduce a held-back window.

## Falsifiers

- `width` wrong → the solve is under/over-determined.
- bits not a clean keystream → no linear solution.
- `predict != held-back` → not a raw LFSR.

## Boundaries

- `berlekamp-massey` gives the taps; `lfsr-recover` uses them to rebuild
  the register — they compose.
- Needs ≥ `w` known keystream bits to place the state (usually ≥2·w via BM).
