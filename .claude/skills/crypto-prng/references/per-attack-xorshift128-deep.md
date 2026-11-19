# per-attack xorshift128 deep — the 4-word state solve

## The tool

```bash
python3 tools/crypto/xorshift128.py --outs o0,o1,o2,o3 --predict n
python3 tools/crypto/xorshift128.py --selftest
```

A standalone `tools/crypto/` CLI — NOT a `crypto_attack.py` id.
`--outs` ≥4 consecutive words; `--predict n` the next `n`.

## The math

xorshift128's state is four words `(x,y,z,w)`; `G` emits `w` each call.
Four consecutive outputs = the full 128-bit state (the `w` history IS the
register). The tool solves the linear system and rolls forward.

## The count floor

4 consecutive words. `<4` → underdetermined. `≥5` → verification.

## The variant trap — the most common failure

| Variant | Recurrence | Covered |
|---|---|---|
| `xorshift128` | `x^(x<<11)`, rotate, `w^(w>>19)^(t>>8)` | YES |
| `xorshift128+` | `s0+s1`, `<<23`/`>>17`/`>>26` | NO — `Math.random` |
| `xorshift64*` | `*C` output | NO |
| `xoroshiro`/`xoshiro` | rotations | NO |

`Math.random` in V8 = `xorshift128+` + a `double` — `xorshift128.py`
returns a wrong state → `predict != held`.

## The output-shape traps

- `Math.random` doubles — `[0,1)` floats, the `+` variant.
- non-consecutive — the linear solve needs alignment.
- a reseeding oracle — each output a fresh seed.

## The verification

`--predict 1` vs a held-back 5th word — `predict == held`.

## Expected signal / falsifier

- **Expected**: `predict == held`.
- **Falsifier**: `predict != held` → wrong variant / non-consecutive.
