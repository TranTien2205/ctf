# Per-attack `lcg-truncated` — the card

## Trigger

LCG where each output leaks only the HIGH bits (low `b` bits dropped), and
`m`, `a`, `c` are known. Family `prng-lattice`.

## Command

```bash
python3 tools/crypto_attack.py lcg-truncated \
  --outputs h0,h1,... --modulus m --a a --c c --low-bits b
```

`--low-bits` is the number of DROPPED bits, not kept.

## Mechanism

The dropped low bits are the hidden part — an HNP-style lattice over
`lcg.truncated_lcg_recover`/`lll.py` recovers the state.

## Verify

`predict == held-back` after recovering the state.

## Falsifiers

- `m`,`a`,`c` not all known → can't build the lattice.
- `predict != held-back` → the truncation shape or `--low-bits` wrong.
- Kept bits too few → lattice has no short vector.

## Boundaries

- `--low-bits` counts the DROPPED low bits — off-by-one kills it.
- The leak must be `floor(x / 2^b)` — high bits; if the leak is `x mod 2^k`
  it's a different problem (low bits leak, not high).
- Needs enough outputs that the lattice converges (the `required` heuristic).
