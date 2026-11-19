# lcg-truncated deep — only the high bits leak

## The attack id

```bash
python3 tools/crypto_attack.py lcg-truncated \
  --outputs h0,h1,... --modulus m --a a --c c --low-bits b
```

All of `--modulus`, `--a`, `--c`, `--low-bits` are REQUIRED. The leak is
`h_i = x_i >> b` — the high bits of each state.

## The setup

The oracle never gives `x_i` — it gives `h_i`, the top `32-b` bits. The
dropped `b` bits `l_i = x_i mod 2^b` are small but unknown:

```
x_i = h_i·2^b + l_i,    0 ≤ l_i < 2^b
```

With `a`,`c`,`m` known, each `x_{i+1}=a·x_i+c` is a linear equation whose
unknown `l_i`,`l_{i+1}` are bounded — a Hidden-Number problem. Build the
lattice over several outputs; the true `(l_0,...,l_k)` is the short vector.
`lcg-truncated` runs that lattice.

## The `--low-bits` trap — the #1 operator error

`--low-bits` is the count of DROPPED bits `b`, NOT the kept bits.
`x_i >> 32` on a 64-bit state → `low-bits = 32`. `x_i >> 16` on a 48-bit
`java.util.Random` state → `low-bits = 16`. Pass the kept count and the
lattice is built for the wrong bound → `predict != held`.

## Why `a`,`c`,`m` must be known

The lattice uses the recurrence's exact constants. If `m`/`a`/`c` are
also unknown, this attack does not apply — first recover them (you'd need
a different leak). In a truncated challenge the params are given or
readable in source.

## The output count

The `required` heuristic — enough `h_i` that the lattice's bound forces a
unique short vector. More `h_i` → a better-conditioned lattice. The tool
prints `required`; aim for that many plus a held-back output.

## The `java.util.Random` case

`java.util.Random` is an LCG: `m = 2^48`, `a = 0x5DEECE66D`, `c = 0xB`,
and `nextInt()`/`nextLong()` leak `x >> 16` (the top bits of the 48-bit
state). The canonical `lcg-truncated` target:

```bash
python3 tools/crypto_attack.py lcg-truncated \
  --outputs <leaks> --modulus 281474976710656 \
  --a 25214903917 --c 11 --low-bits 16
```

## The failure modes

- `low-bits` wrong → the bound is wrong → no short vector / wrong state.
- `a`/`c`/`m` wrong → the recurrence is wrong → `predict != held`.
- too few `h_i` → the lattice is under-determined → gather more.
- the leak isn't `x>>b` (it's `x mod n`, `x & mask`) → wrong shape → the
  lattice model is wrong.

## The verification

`predict_next` on a held-back `h_{k}` — the predicted state's high bits
must equal the held-back leak.

## Expected signal / falsifier

- **Expected signal**: the recovered `l_i`, the full `x_i`, `predict ==
  held`.
- **Falsifier**: `predict != held` → `low-bits`/`a`/`c`/`m`/shape wrong.
