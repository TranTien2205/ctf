# RSA: pick the attack from what you're given

The handout decides the attack — never brute-force. Read the given numbers
first, then take exactly one row.

## Given → attack

| Given | Attack | One-liner |
|---|---|---|
| `e=3` (or tiny e), `c` only, small `m` | direct root | `m = c^(1/e)` exact root — `gmpy2.iroot` |
| `e=3`, same `m` to ≥3 recipients | Håstad broadcast | CRT combine the c's, then `iroot` |
| `p` and `q` in the source | immediate | `d = inverse(e, (p-1)(q-1))` |
| `phi` or `d` given | immediate | skip the math |
| `N` and `d` both public | recover p,q | `ed-1 = k*phi` — factor N from d |
| `N` factorable | factor it | `factordb`, `yafu`, `RsaCtfTool` |
| `p`,`q` close together | Fermat | `p,q` near `sqrt(N)` — `sympy.isqrt` + walk |
| `dp` or `dq` leaked | small-dp attack | `e*dp - 1 = k(p-1)`, k < e |
| `d` small (d < N^0.25-ish) | Wiener | continued fractions on `e/N` |
| `d` medium | Boneh-Durfee | `d < N^0.292` — `RsaCtfTool` |
| same `N` different `e`, same `m` | common modulus | `gcd(e1,e2)` bezout combine |
| `N` reused across `m` (`m1`,`m2` gcd) | gcd attack | `gcd(N1,N2)` shares p |
| padding oracle (server answers valid/invalid) | Bleichenbacher | oracle + `2B` bounds walk |
| `e=65537`, standard `m`, big `c` | not this class | the bug is elsewhere — look at padding/signature/key reuse |

## Working it

```python
from Crypto.Util.number import long_to_bytes, inverse
import gmpy2
p, q = ...                       # from whichever row matched
phi = (p-1)*(q-1)
d = inverse(e, phi)
m = pow(c, d, p*q)
print(long_to_bytes(m))
```

`RsaCtfTool` covers most rows: `python3 RsaCtfTool.py --publickey key.pem
--uncipherfile c.bin [--attack fermat|wiener|boneh_durfee|...]`.

## Falsifier

The numbers are all correct-size, `N` doesn't factor on `factordb`, no small-
`e`/`d`/`p`/`q`/`dp`/`phi`/`oracle` is given — the break is not in the RSA
parameters; look at *how it's used* (padding, signature verification, key
reuse, RNG seeding the primes).

## Traps

- `factordb.com` before any math — a trivially-factored `N` is the most common
  CTF RSA problem and the tool does it in one call.
- `m = c^(1/e)` only works when `m^e < N` — check `c < N` and `e` is 3 first.
- CRT `m^e mod N_i` broadcast needs *different* N's on the same m.
- PEM/DER key files are easier than numbers — extract `n`, `e` with
  `openssl rsa -pubin -text` before doing anything else.
