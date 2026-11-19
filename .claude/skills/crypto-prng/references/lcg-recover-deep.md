# lcg-recover deep — `m` known, `a`,`c` unknown

## The attack id

```bash
python3 tools/crypto_attack.py lcg-recover --outputs o0,o1,o2 --modulus m
```

`--outputs` = comma-separated consecutive raw outputs.
`--modulus` = the known modulus `m`.

## The math

Given three consecutive raw states `x0,x1,x2` of `x_{i+1}=a·x_i+c mod m`:

```
x1 = a·x0 + c   (mod m)
x2 = a·x1 + c   (mod m)
x2 - x1 = a·(x1 - x0)   (mod m)
a = (x2 - x1) · (x1 - x0)^{-1}   (mod m)
c = x1 - a·x0                    (mod m)
```

One inversion, one multiply — `a`,`c` fall out in O(log m). With `a`,`c`
the entire stream, forward and backward, is deterministic.

## The precondition — the only obstruction

`a`'s formula needs `(x1 - x0)^{-1} mod m`, which exists iff
`gcd(x1 - x0, m) = 1`.

- `m` a power of two (`2^31`, `2^32`) — every even difference fails the
  inverse. Gather outputs until some consecutive difference is ODD.
- `m` composite — factor it, recover `a` mod each prime power, CRT.
- `m` prime — the difference is invertible unless `x1 == x0` (a fixed
  point — essentially impossible in a real LCG).

## The output-shape trap

`--outputs` wants the RAW state outputs. If the oracle leaks `x mod n`,
`x >> b`, or a float, the values you feed are NOT `x_i` — the affine solve
returns wrong `a`,`c`. Normalize or change attack (`lcg-truncated`).

## The count

3 outputs minimum. More outputs let you verify: `a`,`c` recovered from
`o0,o1,o2` must reproduce `o3` — an instant falsifier.

## The verification

```python
x_next = (a * o_last + c) % m
assert x_next == held_back      # never skip
```

## Expected signal / falsifier

- **Expected signal**: `{a, c, next}` and `next == held-back`.
- **Falsifier**: `gcd(x1-x0, m) != 1` for every triple, or `predict !=
  held` → not a plain LCG / wrong `m` / wrong normalization.

## The chain

`lcg-recover` → `a`,`c` → `predict_next` → the next token/roll/key → the
flag-object (an authenticated call, a decrypted stream, a won game).

## Backward prediction

`x_i = a^{-1}·(x_{i+1} - c) mod m` — recover past outputs too. Useful when
the flag-object was minted BEFORE your first observed output.
