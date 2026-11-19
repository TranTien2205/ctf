# per-attack lcg-recover deep — the closed-form solve

## The command

```bash
python3 tools/crypto_attack.py lcg-recover --outputs o0,o1,o2 --modulus m
```

## The derivation

```
x1 = a·x0 + c   (mod m)
x2 = a·x1 + c   (mod m)
x2 - x1 = a·(x1 - x0)   (mod m)
a = (x2 - x1) · (x1 - x0)^{-1}   (mod m)
c = x1 - a·x0                  (mod m)
```

## The obstruction — the only one

`(x1-x0)` must be invertible mod `m`: `gcd(x1-x0, m) == 1`.

- `m` a power of 2 (`2^31`,`2^32`,`2^48`) — an EVEN difference can't
  invert. Gather outputs until a consecutive difference is ODD.
- `m` composite — factor `m`, solve mod each prime power, CRT.
- `m` prime — any nonzero difference inverts.

## The rawness trap — the most common failure

`--outputs` wants raw `x_i`. Feeding `x mod n`, `x>>b`, floats, hex
strings, or `randint` outputs returns wrong `a`,`c` — the affine
structure you solved isn't the real one. Normalize first.

## The verification

```python
x_next = (a * outputs[-1] + c) % m
assert x_next == held_back      # the only accept
```

A wrong `a`,`c` can interpolate `o0,o1,o2` — the held-back check is
mandatory.

## The backward direction

`x_i = a^{-1}·(x_{i+1} - c) mod m` — recover past outputs (e.g. the
flag-object minted before your first observation).

## The known-`m` values

`2^31`/`2^32` (rand), `2^48` (java), `2^31-1` (minstd), or the `MOD`/
`modulus` in source.

## Expected signal / falsifier

- **Expected**: `{a,c,next}`, `next == held`.
- **Falsifier**: `gcd(x1-x0,m)!=1` everywhere / `predict != held` → wrong
  `m` / non-raw inputs / not a plain LCG.
