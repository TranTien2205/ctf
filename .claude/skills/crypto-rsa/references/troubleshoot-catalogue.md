# Troubleshoot catalogue — failure → the read → the next step

## The slow failures

| Symptom | The read | The fix |
|---|---|---|
| LLL slow | `lll_backend` | pure-python LLL; budget + `m`,`t` |
| `fermat` long | `|p-q|` large | `--max-iters`; route `pollard-pm1`/leak |
| `pollard-pm1` long | `B` large | `a^{B!}` is `O(B)` |

## The no-find failures

| `wiener`/`boneh-durfee` no-find | `d≥n^0.25`/`n^0.292` | the bound |
| `coppersmith` no-find | window `< n^0.25`/`n^(1/e)` | the leak |
| `fermat` no square | `|p-q|` too large | the bound |
| `hastad` root fails | `<e` n's / pad | the shape |
| `common-modulus` `m^gcd` | `gcd>1` | `nth-root` on `m^gcd` |
| `pollard-pm1` `gcd=1` | `p-1` not `B`-smooth | raise `B` |
| `franklin-reiter` no linear gcd | not `a·m1+b` | the relation |
| `batch-gcd` all `gcd=1` | no shared `p` | the count ≠ the bug |
| `eth-root` `gcd=1` | a normal `inverse` | `rsa-decrypt` |

## The verify failures

| `pow(m,e,n)≠c` | wrong `m`/root | other `g` candidates, the pad |
| `p*q≠n` | false split | the `gcd` was 1 |
| `pow(c,d,n)`≠`m` | wrong `d`/`phi` | the value held is wrong |

## The class failure

Every bound met → no RSA violation → `crypto-symmetric-oracle`,
`crypto-ecc-dlog`, `crypto-prng`, `web-*` — `class-boundary.md`.

## The tool failure

`crypto_attack.py <id> --help` — the real flags; `franklin-reiter` is
`tools/crypto/franklin_reiter.py`, the `sig`/`dp` recoveries are manual.
