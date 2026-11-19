# xorshift128 recover deep — the 4-word clone

## The tool

```bash
python3 tools/crypto/xorshift128.py --outs o0,o1,o2,o3 --predict 5
python3 tools/crypto/xorshift128.py --selftest
```

A standalone `tools/crypto/` module — NOT a `crypto_attack.py` id.
`--outs` = ≥4 comma-separated consecutive 32-bit outputs. `--predict n` =
emit the next `n`. `--selftest` proves it offline.

## The math

xorshift128's state is four words `(x,y,z,w)`. Each call:

```
t = x ^ (x<<11);  x,y,z = y,z,w
w = w ^ (w>>19) ^ t ^ (t>>8);  output w
```

The output IS `w` each call — so four consecutive outputs carry the state
in disguise: `(o0,o1,o2,o3)` determine `(x,y,z,w)` up to the rotation,
which the linear solve fixes. The tool sets up that system and rolls
forward.

## The count floor

4 consecutive words minimum. Fewer → underdetermined (the 128-bit state
isn't pinned). More → verification.

## The variant trap — the most common failure

| Variant | Recurrence | Covered? |
|---|---|---|
| `xorshift128` | `x^(x<<11)`, `w>>19`, `t>>8` | YES — this tool |
| `xorshift128+` | two-word `s0+s1`, `<<23`/`>>17`/`>>26` | NO — V8 `Math.random` |
| `xorshift64*` | one word, multiply output | NO |
| `xoroshiro`/`xoshiro` | rotations | NO |

`Math.random` in V8 is `xorshift128+` — the `+` variant. Feeding a `128+`
stream to `xorshift128.py` returns a wrong state — `predict != held`.

## The output-shape traps

- **`Math.random()` doubles** — `[0,1)` floats, not raw words — plus `128+`.
- **non-consecutive** — the linear solve needs alignment.
- **64-bit / rotated variants** — different algorithm.

## The seed-search fallback

If 4 outputs aren't available but the seed is small (a challenge often
seeds `xorshift` with a known/derivable seed), bound and enumerate —
`per-family-seed`.

## The verification

`--predict 1` against a held-back 5th output. `predict == held`.

## Expected signal / falsifier

- **Expected signal**: `predict == held`.
- **Falsifier**: `predict != held` → wrong variant (`128+`/64*/rotating)
  or non-consecutive outputs. Fingerprint the variant.
