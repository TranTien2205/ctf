# Falsifiers deep — the closing observation, per attack

## The gcd falsifiers

| Observation | Kills | The file |
|---|---|---|
| `gcd(ni,nj)=1` all pairs | `batch-gcd` | `batch-gcd*.md` |
| `gcd(e1,e2)>1` | `common-modulus` | `common-modulus*.md` |
| `gcd(a^{B!}-1,n)=1` at `B` | `pollard-pm1` at `B` | `pollard-pm1*.md` |
| `gcd(s'^e-m,n)=1` | `crt` Bellcore | `crt*.md` |
| `gcd(pow(a,e·dp-1,n)-1,n)=1` | `crt` dp | `crt*.md` |

## The bound falsifiers

| Observation | Kills | The file |
|---|---|---|
| `d ≥ n^0.25` | `wiener` | `wiener*.md`,`lattice-bounds.md` |
| `d ≥ n^0.292` | `wiener`+`boneh-durfee` | `boneh-durfee*.md`,`boundary-cases*` |
| window `< n^0.25` | `coppersmith-high-bits`/`-core` | `coppersmith*.md` |
| window `< n^(1/e)` | `coppersmith` partial-message | `coppersmith*.md` |
| `m^e ≥ n` | `small-e-root`/`nth-root` | `small-e-root*.md`,`nth-root*.md` |
| `<e` n's / `∏n<m^e` / pad | `hastad` | `hastad*.md` |
| `|p-q|` too large (`a` budget) | `fermat` | `fermat*.md` |
| `p-1` not `B`-smooth | `pollard-pm1` | `pollard-pm1*.md` |

## The relation falsifiers

| Observation | Kills |
|---|---|
| `m2` not `a·m1+b` | `franklin-reiter` |
| `∏pi ≤ m` / no fault / inconsistent `dp`,`dq`,`qInv` | `crt` |
| `gcd(e,phi)=1` | `eth-root` — normal `inverse` |
| `d`/`phi` fails `pow`/`p*q` | `factor-from-d`/`rsa-decrypt` wrong input |

## The class falsifier

Every bound on the sheet met → **no RSA violation** — the bug is in the
protocol (`crypto-symmetric-oracle`), the curve (`crypto-ecc-dlog`), a stream
(`crypto-prng`), or the web layer (`web-*`). `class-boundary.md`.

## The record

A falsifier observed → `knowledge/attempts/<challenge>.json` +
`negative-results.md` + `../field-notes.md`. The falsifier is the *evidence* the
attack is closed — not a retry trigger.
