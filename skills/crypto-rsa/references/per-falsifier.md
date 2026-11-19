# Per-falsifier map — the closing observation → what it kills

## The gcd falsifiers

| Observation | Kills |
|---|---|
| `gcd(ni,nj)=1` all pairs | `batch-gcd` |
| `gcd(e1,e2)>1` | `common-modulus` |
| `gcd(a^{B!}-1,n)=1` | `pollard-pm1` at `B` |
| `gcd(s'^e-m,n)=1` | `crt` Bellcore |
| `gcd(pow(a,e·dp-1,n)-1,n)=1` | `crt` dp |

## The bound falsifiers

| Observation | Kills |
|---|---|
| `d ≥ n^0.25` | `wiener` |
| `d ≥ n^0.292` | `wiener` + `boneh-durfee` |
| window `< n^0.25` | `coppersmith-high-bits`/`-core` |
| window `< n^(1/e)` | `coppersmith` partial-message |
| `m^e ≥ n` | `small-e-root`/`nth-root` |
| `∏ni < m^e` / `<e` n's / a pad | `hastad` |
| `|p-q|` too large (`a` budget out) | `fermat` |

## The relation falsifiers

| Observation | Kills |
|---|---|
| `m2` not `a·m1+b` | `franklin-reiter` |
| `∏pi ≤ m` / no fault / inconsistent `dp`,`dq`,`qInv` | `crt` |

## The leak falsifiers

| Observation | Kills |
|---|---|
| `d`/`phi` fails `pow`/`p*q` | `factor-from-d`/`rsa-decrypt` — wrong input |
| `gcd(e,phi)=1` | `eth-root` — normal `inverse` |
| a field redacted *fully* | that field's attack |

## The class falsifier

Every bound on the sheet met → **no RSA violation** — the bug is in the
protocol (`crypto-symmetric-oracle`), the curve (`crypto-ecc-dlog`), a stream
(`crypto-prng`), or the web layer. `class-boundary.md`.

## The record

A falsifier observed → `knowledge/attempts/<challenge>.json` + a `negative-results`
entry + `../field-notes.md`. The falsifier is the *evidence* the attack is closed.
