# per-attack lcg-truncated deep — the Hidden-Number lattice

## The command

```bash
python3 tools/crypto_attack.py lcg-truncated \
  --outputs h0,... --modulus m --a a --c c --low-bits b
```

All of `--modulus`, `--a`, `--c`, `--low-bits` required.

## The setup

The leak `h_i = x_i >> b` gives the high bits; `x_i = h_i·2^b + l_i`
where `l_i = x_i mod 2^b` is small (`<2^b`). With `a`,`c`,`m` known, each
`x_{i+1}=a·x_i+c` is a linear equation whose unknowns `l_i` are bounded —
a Hidden-Number Problem. The lattice over `k` outputs closes when the
bound forces a unique short vector.

## The `--low-bits` trap — the #1 error

`--low-bits` = the DROPPED bits `b`, NOT the kept bits.

- `x_i >> 32` on a 64-bit state → `low-bits = 32`.
- `x_i >> 16` on `java.util.Random`'s 48-bit state → `low-bits = 16`.
- `x_i >> 17` on `drand48` → `low-bits = 17`.

Passing the kept count builds a lattice for the wrong bound → no short
vector / wrong state.

## The count — `required`

The tool prints `required` — enough `h_i` that the bound `l_i<2^b` forces
a unique short vector. Collect `required`+ and hold one back.

## The `java.util.Random` canonical case

```bash
python3 tools/crypto_attack.py lcg-truncated \
  --outputs <nextInt leaks> --modulus 281474976710656 \
  --a 25214903917 --c 11 --low-bits 16
```

`m=2^48`, `a=0x5DEECE66D`, `c=0xB`, `nextInt`=`x>>16`.

## The shape trap — `>>b` vs `mod n`

`lcg-truncated` is for `x>>b` (HIGH bits kept, low dropped). `x mod n`
/`x & mask` is a DIFFERENT structure — reduced, not truncated — the
lattice model doesn't apply.

## The failure modes

- `low-bits` wrong → wrong bound.
- `a`/`c`/`m` wrong → wrong recurrence.
- too few `h_i` → underdetermined.
- the leak isn't `x>>b` → wrong model.

## Expected signal / falsifier

- **Expected**: the recovered `l_i`/state, `predict == held`.
- **Falsifier**: `predict != held` → `low-bits`/params/shape wrong.
