# LCG deep — the linear congruential generator, end to end

## The definition

```
x_{i+1} = (a·x_i + c) mod m
```

- `x_i` — the internal state (and, in the simplest leak, the output).
- `a` — the multiplier.
- `c` — the increment.
- `m` — the modulus.

The output equals the state only in the simplest leak. A real generator
usually outputs `x_i mod n`, `x_i >> b`, or `f(x_i)` — normalize first.

## Why the state is recoverable

The recurrence is **affine in the state**. One unknown `x_i` plus known
`a,c,m` is a single modular equation — trivially solvable. With `a,c` also
unknown, three consecutive outputs pin them; with `m` unknown too, six
outputs pin all three.

## `lcg-recover` — `m` known, `a`,`c` unknown

Given `x0,x1,x2`:

```
a = (x2 - x1) · (x1 - x0)^{-1}  mod m
c = (x1 - a·x0)                 mod m
```

The only obstruction is `gcd(x1-x0, m) != 1` — the inverse of `(x1-x0)`
does not exist. Then either gather another triple (a different difference
may invert) or factor `m` and work mod each prime.

```bash
python3 tools/crypto_attack.py lcg-recover --outputs x0,x1,x2 --modulus m
```

- Expected signal: JSON `{a, c, next}` and `predict_next == held-back`.
- Falsifier: non-invertible difference / `predict != held`.

## `lcg-unknown-modulus` — `m` also unknown

The telescope trick. Let `t_i = x_{i+1} - x_i`. Then:

```
t_{i+1} = a·t_i (mod m)   →   t_{i+1}·t_{i-1} - t_i^2 ≡ 0 (mod m)
m divides gcd over i of (t_{i+1}·t_{i-1} - t_i^2)
```

So `m | gcd(...)`. Usually `m` equals that gcd (up to small multiples).
Then feed the recovered `m` into `lcg-recover`.

```bash
python3 tools/crypto_attack.py lcg-unknown-modulus --outputs o0,o1,o2,o3,o4,o5
```

- Needs ≥6 outputs for a stable gcd.
- Expected signal: a plausible `m` (power of two / product).
- Falsifier: gcd collapse to 0 or 1 → not an LCG / too few outputs.

## `lcg-truncated` — only high bits leak

The leak is `h_i = x_i >> b` — the low `b` bits are dropped. `m`,`a`,`c`
must be known (from source). The state `x_i = h_i·2^b + l_i` with `l_i`
small — a Hidden-Number/lattice problem. More outputs shrink the lattice
until the true `l_i` (hence `x_i`) is the short vector.

```bash
python3 tools/crypto_attack.py lcg-truncated \
  --outputs h0,h1,... --modulus m --a a --c c --low-bits b
```

- `--low-bits` is the DROPPED bit count `b` (NOT the kept bits — the most
  common operator error).
- `m`,`a`,`c` are all REQUIRED.
- Expected signal: a recovered full state, `predict_next` correct.
- Falsifier: `predict != held` — wrong `low-bits` or params.

## The known-moduli cheat sheet

| `m` | Source |
|---|---|
| `2^31` | glibc `rand()` (old) |
| `2^32` | `rand()` returning full word |
| `2^48` | `java.util.Random` (`a=0x5DEECE66D`, `c=0xB`) |
| `2147483647` (`2^31-1`) | `minstd`/`park-miller` (`a=16807`, `c=0`) |

`java.util.Random.nextInt` leaks `x >> (48-32)` = high 32 of a 48-bit
state — the `lcg-truncated` shape with `low-bits = 16`.

## The verification

Never record `a,c,m` from a return value alone. Hold back one output,
predict it, compare. `predict == held` is the only accept signal.
