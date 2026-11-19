# Probe map — the read → the signal → the attack → the file

| The read | The signal | The attack | The file |
|---|---|---|---|
| `n` count ≥2 | multi | `batch-gcd`/`hastad` | `batch-gcd*.md`,`hastad*.md` |
| `e` count 2 on 1 `n` | two `e` | `common-modulus` | `common-modulus*.md` |
| `e` small | `e`=3/5/17 | `small-e`/`hastad`/`franklin-reiter` | `small-e-root*.md`,`hastad*.md` |
| `e`≈`n` | small `d` | `wiener`/`boneh-durfee` | `wiener*.md`,`boneh-durfee*.md` |
| `gcd(e,phi)>1` | no inverse | `eth-root` | `eth-root*.md` |
| `n` square/prime | degenerate | `phi` | `edge-cases*.md` |
| `m^e<n` | wrap | `small-e`/`nth-root` | `small-e-root*.md` |
| `keygen` `next_prime` | close `p,q` | `fermat` | `fermat*.md` |
| `keygen` `seed` | weak RNG | `batch-gcd` | `batch-gcd*.md` |
| `keygen` `p-1` smooth | smooth `p-1` | `pollard-pm1` | `pollard-pm1*.md` |
| `keygen` `a·m1+b` | linear `m` | `franklin-reiter` | `franklin-reiter*.md` |
| `keygen` `dp`,`qInv` | CRT leak | `crt` | `crt*.md` |
| `keygen` `d`/`phi`/`redact` | a leak | `factor-from-d`/`coppersmith`/`crt` | `factor-from-d*.md` |

## The verify

`pow(m,e,n)==c` / `p*q==n`.
