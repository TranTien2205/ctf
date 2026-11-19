# nth-root deep — the general e-th root, the full treatment

## The mechanism

`c = m^e` exactly (the wrap never happened) for a general `e`. `m = c^{1/e}` —
`integer_nthroot(c, e)`. The same wrap attack as `small-e-root` but for an
arbitrary exponent.

## Detection

- `e` = 3, 5, 17, 257, or any small value.
- `m^e < n` — the wrap condition.
- A `c` that is an exact `e`th power.

## The bound / falsifier

`m^e < n`. `m^e ≥ n` → `c` is modular → `nth-root` fails → `hastad`/`coppersmith`.

## The attack

```bash
crypto_attack.py nth-root --x <x> --n <n>
```

`--x` is the value to take the `n`th root of; `--n` is the root degree. Or
`small-e-root --n <n> --e <e> --c <c>` which wraps `nth-root` for the RSA case.

```python
m, exact = integer_nthroot(c, e)
assert exact and pow(m, e) == c
```

## The verify

`pow(m,e)==c` — plain.

## Variants

- `small-e-root` — the RSA-shaped wrapper (`--n --e --c`).
- A wrapped `m` → `hastad`/`coppersmith`.

## The honest status

Standard — catalogue.
