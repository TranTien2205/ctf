# xorshift deep — the xorshift family, end to end

## The definition

xorshift128 state = four 32-bit words `x,y,z,w`. Per call:

```
t = x ^ (x << 11)
x = y; y = z; z = w
w = w ^ (w >> 19) ^ t ^ (t >> 8)
output w
```

The whole state is 128 bits. Output is `w` — a pure word.

## Why 4 consecutive words are fatal

The recurrence is linear over GF(2) with a 128-bit state. 4 consecutive
32-bit outputs = the full 128-bit state (modulo the rotation order) —
solve the linear system or, since `w` is output each step, the four most
recent `w` values ARE the state in disguise. `xorshift128.py` recovers
it and rolls forward.

## `xorshift128` — the CLI

```bash
python3 tools/crypto/xorshift128.py --outs o0,o1,o2,o3 --predict 5
python3 tools/crypto/xorshift128.py --selftest
```

- `--outs` = ≥4 comma-separated consecutive 32-bit outputs.
- `--predict n` = emit the next `n` outputs.
- `--selftest` = prove the module offline.
- **Not a `crypto_attack.py` id** — it's a standalone `tools/crypto/`
  module with its own CLI.

## The variant trap — the most common failure

xorshift has a family — wrong variant = wrong recovery:

| Variant | Recurrence | Status |
|---|---|---|
| `xorshift128` | 4×32-bit, shifts 11/19/8 | **`xorshift128.py` covers this** |
| `xorshift128+` | two-word, `s1^(s1<<23)` etc, output `s0+s1` | NOT covered — `Math.random` in V8 |
| `xorshift64*` | one word, `*C` output | NOT covered |
| `xoroshiro`/`xoshiro` | rotations | NOT covered |

`Math.random` in V8/Chrome is `xorshift128+` — the `+` variant — and its
output passes through a `double` conversion. `xorshift128.py` on a
`128+` stream gives a wrong state; fingerprint the variant first
(`detection-deep.md`).

## The output-shape traps

- **`Math.random()`** returns a `double` in `[0,1)` — `128+` plus a float
  conversion, not a raw `w`.
- **`xorshift64`/`xoroshiro`** — different width/variant.
- **non-consecutive outputs** — the linear solve needs alignment.

## The seed-search alternative

If the challenge seeds `xorshift` with a small value, bound the window
and enumerate — same playbook as `per-family-seed.md`.

## The verification

`--predict 1` against a held-back 5th output. `predict == held` is the
only accept.
