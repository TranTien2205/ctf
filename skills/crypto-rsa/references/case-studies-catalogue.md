# Case studies catalogue — the challenge shapes, indexed

## The single-modulus shapes

| The shape | The attack | The file |
|---|---|---|
| `q=next_prime(p)` | `fermat` | `fermat*.md`,`case-studies-deep.md` |
| `d` small, `e`≈`n` | `wiener`/`boneh-durfee` | `wiener*.md`,`boneh-durfee*.md` |
| `e`=3,`m` short | `small-e-root` | `small-e-root*.md` |
| `p-1` smooth | `pollard-pm1` | `pollard-pm1*.md` |
| `p` partial leak | `coppersmith-*` | `coppersmith*.md` |
| `d`/`phi`/`dp` leak | `factor-from-d`/`crt` | `factor-from-d*.md`,`crt*.md` |
| `gcd(e,phi)>1` | `eth-root` | `eth-root*.md` |
| `n`=p²/prime/multi | degenerate `phi` | `edge-cases*.md` |

## The multi-modulus shapes

| The shape | The attack | The file |
|---|---|---|
| a `.json`/list of `n` | `batch-gcd` | `batch-gcd*.md` |
| same `m`,`e` n's | `hastad` | `hastad*.md` |
| 2 `e` on 1 `n` | `common-modulus` | `common-modulus*.md` |

## The relation shapes

| The shape | The attack | The file |
|---|---|---|
| `m2=a·m1+b` | `franklin-reiter` | `franklin-reiter*.md` |
| residues `mod pi` | `crt` | `crt*.md` |
| correct+faulty `sig` | `crt` Bellcore | `crt*.md` |

## The verify

Every shape ends at `pow(m,e,n)==c` or `p*q==n` — the gate.

## The honest status

Catalogue — no local solve. `case-studies-deep.md` has the annotated shapes;
`worked-examples*.md` has the full solves; `scenarios.md` the presentations.
