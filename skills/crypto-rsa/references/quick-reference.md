# Quick reference — the commands, the bounds

## The one-liner

`crypto_attack.py list` → signal → bound → `crypto_attack.py <id>` →
`pow`/`p*q` verify.

## The signal → attack

| Signal | Command | Bound |
|---|---|---|
| `|p-q|` small | `fermat --n` | `|p-q|` |
| `e`=3,`m³<n` | `small-e-root --n --e --c` | `m^e<n` |
| `e`≈`n`,`d` small | `wiener`/`boneh-durfee --n --e` | `n^.25`/`n^.292` |
| `n`s share `p` | `batch-gcd --moduli` | `gcd>1` |
| `p-1` smooth | `pollard-pm1 --n --b` | `B`≥factor |
| `p` bits | `coppersmith-high-bits --n --known --bits` | `n^0.25` |
| `e` n's same `m` | `hastad --pairs --e` | `≥e` n's |
| 2 `e` on `n` | `common-modulus --n --e1 --c1 --e2 --c2` | `gcd=1` |
| `d`/`phi` | `factor-from-d --n --e --d` | held |
| `p`,`q` | `rsa-decrypt --n --e --c --p --q` | held |
| `gcd(e,phi)>1` | `eth-root --c --e --factors` | `gcd>1` |
| `m2=a·m1+b` | `tools/crypto/franklin_reiter.py` | linear |
| `sig` fault/`dp` | `crt` manual | the relation |

## The verify

`pow(m,e,n)==c` / `p*q==n` / `pow(c,d,n)==m`.
