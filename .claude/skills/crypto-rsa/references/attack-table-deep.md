# Attack table deep — the discriminator, full

## The decision table (read top-down; first yes wins)

| # | If you have | Attack id | Bound / falsifier | Verify |
|---|---|---|---|---|
| 1 | `d`, `phi`, `dp`, or `p`,`q` held | `factor-from-d` / `rsa-decrypt` | the value is real | `p*q==n` / `pow==c` |
| 2 | ≥2 moduli, same gen | `batch-gcd` | a collision exists | `p*q==n` |
| 3 | same `m`, `e` coprime `n` | `hastad` | `≥e` n's, `∏n>m^e`, no pad | `pow(m,e)==x` |
| 4 | 1 `n`, 2 `e`, `gcd=1` | `common-modulus` | `gcd(e1,e2)=1` | `pow(m,e1,n)==c1` |
| 5 | `p`,`q` close | `fermat` | `|p-q|` small | `p*q==n` |
| 6 | `e`~`n`, `d<n^0.25` | `wiener` | `d<n^0.25` | `pow(c,d,n)==m` |
| 7 | `d<n^0.292` | `boneh-durfee` | `d<n^0.292` | `pow(c,d,n)==m` |
| 8 | `p`-bits / centred guess | `coppersmith-*` | window≥`n^0.25` | `p|n` |
| 9 | `e=3`,`m^3<n` | `small-e-root` | `m^e<n` | `pow(m,e)==c` |
| 10 | `p-1` smooth | `pollard-pm1` | `B`≥largest factor | `gcd=p` |
| 11 | `m2=a·m1+b` | `franklin-reiter` | linear, `a`,`b` known | `pow(m,e,n)==c` |
| 12 | residues/fault/`dp` | `crt` | `∏pi>m`/fault/consistent | `pow==c`/`gcd=q` |
| 13 | `gcd(e,phi)>1` | `eth-root` | `p`,`q` held | `pow`+format |
| 14 | none | reclassify | — | — |

## The rows in order of cost

**Seconds**: `factor-from-d`, `rsa-decrypt`, `eth-root`, `fermat`, `batch-gcd`,
`common-modulus`, `small-e-root`, `nth-root`, `pollard-pm1`, `wiener`, `crt`,
`franklin-reiter`, `hastad`.

**Lattice (slow)**: `boneh-durfee`, `boneh-durfee-escalate`, `coppersmith-core`,
`coppersmith-high-bits`.

## The confusable classes

| Looks like | Actually |
|---|---|
| `g`,`h=g^x`,a curve | `crypto-ecc-dlog` |
| a service that encrypts/decrypts | `crypto-symmetric-oracle` |
| a keystream | `crypto-prng` |
| a classical cipher | `crypto-classical` |

## The escalation within a family

- `wiener` fails → `boneh-durfee` → `boneh-durfee-escalate` (`m`,`t` up) → dead.
- `coppersmith-high-bits` fails → `coppersmith-core` (centred guess) → dead.
- `batch-gcd` empty → per-`n` `fermat`/`wiener`/etc.
- `hastad` `<e` n's → `franklin-reiter`/`coppersmith`.
- `fermat` slow → `pollard-pm1`/a leak.

## The falsifier column

Every bound is the falsifier — `d≥n^0.292`, window `<n^0.25`, `m^e≥n`, `<e` n's,
`gcd>1`, `|p-q|` large, `p-1` not smooth. Exceeded = closed.
