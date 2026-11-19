# Attack table catalogue — the discriminator, fully expanded

## The rows, ordered

| # | The signal | The attack | The bound | The verify |
|---|---|---|---|---|
| 1 | `n` count ≥2, one `e`, same `m`, `e_coprime`, `len≥e` | `hastad` | `≥e` n's | `pow(m,e)==x` |
| 2 | `n` count ≥2, `m2=a·m1+b` | `franklin-reiter` | linear | `pow(m,e,n)==c` |
| 3 | `n` count ≥2, a `gcd` collision | `batch-gcd` | `gcd>1` | `p*q==n` |
| 4 | `e` count 2 on 1 `n`, `gcd=1` | `common-modulus` | `gcd=1` | `pow(m,e1,n)==c1` |
| 5 | `e`=3/5/17, `m^e<n`, no pad | `small-e-root`/`nth-root` | `m^e<n` | `pow(m,e)==c` |
| 6 | `e`≈`n`, `d` small | `wiener`→`boneh-durfee` | `n^.25`/`n^.292` | `pow` |
| 7 | `gcd(e,phi)>1`, `p`,`q` held | `eth-root` | `gcd>1` | `pow`+format |
| 8 | `e`=1 | `c=m` | trivial | `pow` |
| 9 | `|p-q|` small (`next_prime`/`p+k`) | `fermat` | `a` budget | `p*q==n` |
| 10 | `p-1` smooth | `pollard-pm1` | `B`≥factor | `1<p<n`,`p|n` |
| 11 | `p` high/low bits | `coppersmith-high-bits`/`-core` | `n^0.25` | `p|n` |
| 12 | `m` partial | `coppersmith` partial-message | `n^(1/e)` | `pow` |
| 13 | `d`/`phi`/`p`,`q` held | `factor-from-d`/`rsa-decrypt` | the value | `pow`/`p*q` |
| 14 | `dp`,`dq`,`qInv` | `crt` manual | consistent | `p*q==n` |
| 15 | `sig`+`sig_faulty` | `crt` Bellcore | a pair | `gcd==q` |
| 16 | `m mod pi` × several | `crt` residues | `∏pi>m` | `pow` |
| 17 | `n`=p²/prime/smooth/multi | degenerate `phi` | the shape | `pow` |

## The default

`e`=65537, no leak, standard keygen → the bug is a *leak* or a *prime
weakness* — re-read the artifacts.

## The falsifier

Each row's bound is a closing observation — `per-bound.md`,
`negative-results-catalogue.md`.
