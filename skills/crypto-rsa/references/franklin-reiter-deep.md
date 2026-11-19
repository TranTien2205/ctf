# franklin-reiter deep — linearly related messages

## The precondition

Two messages with a known **linear** relation `m2 = a·m1 + b`, encrypted under
the same `n` and small `e` (typically `e=3`). `m2` is `m1` plus a known pad,
nonce, or timestamp.

## The maths

`c1 = m^e`, `c2 = (a·m+b)^e` mod `n`. Both polynomials vanish at `x=m`:

```
f(x) = x^e - c1
g(x) = (a·x + b)^e - c2
```

`gcd(f, g)` over `Z_n[x]` — Euclidean algorithm on polynomials — is the linear
factor `(x - m)` → recover `m`.

## The procedure

```python
# over Z_n[x]:
f = x**e - c1
g = (a*x + b)**e - c2
# poly gcd → (x - m) → m
```

## The tool

```bash
python3 tools/franklin-reiter --n <n> --e <e> --c1 <c1> --c2 <c2> --a <a> --b <b>
```

## The bound / falsifier

- The relation must be **exactly** `m2 = a·m1+b` — `a`,`b` known constants.
- Same `n`, same `e` for both.
- A nonlinear relation or unknown `a`,`b` → dead.

## The verify

`pow(m,e,n)==c1`.

## The traps

- `a`,`b` must be **known** — the pad/nonce linking the messages must be given
  or inferable. A `m2 = m1 + "for tomorrow"` is linear with `a=1`, `b` the offset.
- Nonlinear (e.g. `m2 = reverse(m1)`) → a different Coppersmith-type problem.
- Different `n` → the poly gcd is over the wrong ring — needs the same modulus.
