# eth-root deep — the gcd(e,phi)>1 roots, the full treatment

## The mechanism

`gcd(e, φ) = g > 1` → `e` is not invertible mod `φ` → `m^e` has `g` distinct
`e`th roots mod `n`. With `p`,`q` held, compute the `g_p` roots mod `p` and
`g_q` roots mod `q`, CRT-combine into `g` candidates mod `n`, and `pow`+format
picks the true `m`.

## Detection

- **`inverse(e, phi)` fails** — `gcd(e,phi)>1`. A `ZeroDivisionError`/
  `ValueError` on `pow(e,-1,phi)` is the *signature*, not a bug.
- **`e` even** or `e` sharing a factor with `p-1`/`q-1`.
- **`p`,`q` held** — the candidates are computable.

## The bound / falsifier

`gcd(e,phi)>1` and `p`,`q` held. `gcd=1` → a normal `inverse` → `rsa-decrypt`,
not `eth-root`.

## The attack

```bash
crypto_attack.py eth-root --c <c> --e <e> --factors "<p>,<q>"
```

```python
# manual — the g roots via CRT
# solve x^e = c mod p → g_p roots; mod q → g_q roots
# CRT-combine into g candidates mod n
for m_i in candidates:
    if pow(m_i, e, n) == c and is_flag_format(m_i): print(m_i)
```

## The verify

`pow(m,e,n)==c` + the flag format — `pow` picks the true root among `g`.

## Failure modes

- `gcd(e,phi)=1` — a normal `inverse`.
- `p`,`q` not held — the candidates aren't computable.

## The honest status

Standard — catalogue.
