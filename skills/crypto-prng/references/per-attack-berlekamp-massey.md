# Per-attack `berlekamp-massey` — the card

## Trigger

A bit keystream suspected to be LFSR output, taps unknown — you hold ≥2·w
bits where `w` is the register width.

## Command

```bash
python3 tools/crypto_attack.py berlekamp-massey --bits b0,b1,...
python3 tools/crypto_attack.py berlekamp-massey --keystream-hex <hex>
python3 tools/crypto_attack.py berlekamp-massey --bits-file bits.txt
```

## Mechanism

Returns the **linear complexity** (the register width `w`) and the tap
polynomial in this module's `1`-indexed-from-LSB convention.

## Verify

Feed the taps + width to `lfsr-recover`/`lfsr-predict` → reproduce a
held-back bit window.

## Falsifiers

- Linear complexity ≈ stream length → not an LFSR.
- <2·w bits → the recurrence isn't pinned — need more bits.
- taps predict wrong → wrong width or a combining function, not raw LFSR.

## Boundaries

- The 2·w bound is tight — the recurrence needs enough equations.
- A nonlinear filter/combiner on top of an LFSR → BM returns a high
  complexity — not a plain LFSR.
- `--keystream-hex` gives packed bits; `--bits` gives explicit `0,1,0,...`.
