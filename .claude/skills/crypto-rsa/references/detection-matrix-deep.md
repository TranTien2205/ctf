# Detection matrix deep — every observable × every attack, annotated

## The counts

| n count | e count | c count | The attack | The file |
|---|---|---|---|---|
| ≥2, one `e`, same `m` | 1 small | ≥`e` | `hastad` | `hastad*.md` |
| ≥2, same `m`, `m2=a·m1+b` | 1 small | 2 | `franklin-reiter` | `franklin-reiter*.md` |
| ≥2, a shared `p` | any | any | `batch-gcd` | `batch-gcd*.md` |
| 1, two `e`, same `m` | 2 | 2 | `common-modulus` | `common-modulus*.md` |
| 1 | 1 | 1 | single-modulus | the rest |

## The `e` signal × attack

| `e` | The attack | The read |
|---|---|---|
| 3,5,17,257 | `small-e`/`hastad`/`franklin-reiter` | `m^e<n`? `≥e` n's? `a·m1+b`? |
| 65537 | a leak/the primes/a relation | not an `e`-attack |
| `e`≈`n` | `wiener`/`boneh-durfee` | `d` small |
| `gcd(e,phi)>1` | `eth-root` | `p`,`q` held |
| `e`=1 | `c=m` | trivial |

## The `n` shape × attack

| `n` | The attack |
|---|---|
| `n=p·q`,`|p-q|` small | `fermat` |
| `n=p·q`,`p-1` smooth | `pollard-pm1` |
| `n=p·q`,`p` bits | `coppersmith` |
| `n` = `p²`/prime/multi | degenerate `phi` |

## The leak × attack

| The leak | The attack |
|---|---|
| `p` high/low | `coppersmith-high-bits`/`-core` |
| `m` partial | `coppersmith` partial-message |
| `d`/`phi`/`p`,`q` | `factor-from-d`/`rsa-decrypt` |
| `dp`,`dq`,`qInv` | `crt` manual |
| `sig`+`sig_faulty` | `crt` Bellcore |
| `m mod pi` × several | `crt` residues |

## The relation × attack

| The relation | The attack |
|---|---|
| `m2=a·m1+b` | `franklin-reiter` |
| same `m`, `e` n's | `hastad` |
| `gcd(e1,e2)=1` | `common-modulus` |
