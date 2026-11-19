# Quick reference deep — the commands, the bounds, the chain

## The one-liner

`crypto_attack.py list` → the signal → the bound → `crypto_attack.py <id>` →
`pow(m,e,n)==c`/`p*q==n`.

## The signal → attack

| Signal | Command |
|---|---|
| `|p-q|` small | `fermat --n <n>` |
| `e`=3,`m³<n` | `small-e-root --n --e --c` |
| `e`≈`n`,`d` small | `wiener --n --e` / `boneh-durfee --n --e` |
| `n`s share `p` | `batch-gcd --moduli n1 n2 ...` |
| `p-1` smooth | `pollard-pm1 --n --b` |
| `p` bits | `coppersmith-high-bits --n --known --bits` |
| `e` n's same `m` | `hastad --pairs "n1,c1;..." --e` |
| 2 `e` on `n` | `common-modulus --n --e1 --c1 --e2 --c2` |
| `d`/`phi` | `factor-from-d --n --e --d` |
| `p`,`q` | `rsa-decrypt --n --e --c --p --q` |
| `gcd(e,phi)>1` | `eth-root --c --e --factors` |
| `m2=a·m1+b` | `tools/crypto/franklin_reiter.py` (manual) |
| `sig` fault / `dp` | `crt` manual `gcd`/`e·dp-1` |

## The bound

`d<n^0.25` · `d<n^0.292` · window`n^0.25`/`n^(1/e)` · `m^e<n` · `≥e` n's ·
`gcd=1` · `|p-q|` small · `B`≥factor · `∏pi>m` · linear · `gcd(e,phi)>1` ·
the value held.

## The verify

`pow(m,e,n)==c` / `p*q==n` / `pow(c,d,n)==m` / `1<p<n`,`p|n`.

## The chain

`factor`/`d`/`phi` → `rsa-decrypt --p --q` → `m` → `pow` → the flag.
