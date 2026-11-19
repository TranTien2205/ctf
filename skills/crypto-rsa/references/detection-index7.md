# Detection index7 — the signal index

## The signals → the file

| Signal | The file |
|---|---|
| `e`=3/5/17 | `small-e-root*`,`hastad*`,`franklin-reiter*` |
| `e`≈`n` | `wiener*`,`boneh-durfee*` |
| `gcd(e,phi)>1` | `eth-root*` |
| `n`=p²/prime | `edge-cases*` |
| `n`s share `p` | `batch-gcd*` |
| `p-1` smooth | `pollard-pm1*` |
| `p`/`m` bits | `coppersmith*` |
| `m2=a·m1+b` | `franklin-reiter*` |
| `sig`+fault | `crt*` |
| `m` residues | `crt*` |
| `d`/`phi`/`dp`/`qInv`/`p`,`q` | `factor-from-d*`,`crt*`,`rsa-decrypt*` |
| `|p-q|` small | `fermat*` |
| `e` n's same `m` | `hastad*` |
| 2 `e` on `n` | `common-modulus*` |

## The reads

`detection*.md`,`parameter-sheet*.md`,`recon-order*.md` — the reads that
produce the signals.

## The route

`attack-table*.md` → `per-bound.md` → `crypto_attack.py <id>` → `verify*`.
