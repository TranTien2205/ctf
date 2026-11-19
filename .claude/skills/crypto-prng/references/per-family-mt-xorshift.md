# Per-family MT + xorshift — the wide-state branch

## The two attacks

| Attack | Trigger | Card |
|---|---|---|
| `mt19937-clone` | 624 consecutive 32-bit outputs | `per-attack-mt19937-clone.md` |
| `xorshift128` | 4 consecutive 32-bit outputs | `per-attack-xorshift128.md` |

## The discriminator

```
MT (random.getrandbits etc.) → need 624 raw words → mt19937-clone
xorshift → need 4 words → xorshift128.py (standalone)
```

## The MT invariants

- `--outputs` inline comma-separated OR `--outputs-file`; `--count` for how
  many next outputs.
- The 624 is EXACT — 623 fails (state one word short).
- Raw 32-bit `getrandbits(32)` words — NOT `random.random()` floats or
  `randint`/`choice` mixed values.

## The xorshift invariants

- `--outs` comma-separated 32-bit ints (dec or `0x`); `--predict` next
  count; `--selftest`.
- xorshift128 only — `128+`/`64*`/`xorwow` differ.

## The verify

`predict_next`/`--predict` reproduces a held-back word.

## The boundary

- MT partial window (<624) → not cloneable — need the whole state.
- A `seed()`/`reseed` between outputs → alignment broken.
