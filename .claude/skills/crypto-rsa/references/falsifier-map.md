# Falsifier map — the closing observation → the file

| The falsifier | Kills | The file |
|---|---|---|
| `gcd(ni,nj)=1` all | `batch-gcd` | `batch-gcd*.md` |
| `gcd(e1,e2)>1` | `common-modulus` | `common-modulus*.md` |
| `gcd(a^{B!}-1,n)=1` | `pollard-pm1` | `pollard-pm1*.md` |
| `gcd(s'^e-m,n)=1` | `crt` Bellcore | `crt*.md` |
| `d ≥ n^0.25` | `wiener` | `wiener*.md` |
| `d ≥ n^0.292` | `boneh-durfee` | `boneh-durfee*.md` |
| window `< n^0.25`/`n^(1/e)` | `coppersmith` | `coppersmith*.md` |
| `m^e ≥ n` | `small-e`/`nth-root` | `small-e-root*.md` |
| `<e` n's/`∏n<m^e`/pad | `hastad` | `hastad*.md` |
| `|p-q|` too large | `fermat` | `fermat*.md` |
| `p-1` not `B`-smooth | `pollard-pm1` | `pollard-pm1*.md` |
| relation not `a·m1+b` | `franklin-reiter` | `franklin-reiter*.md` |
| `∏pi≤m`/no fault/inconsistent | `crt` | `crt*.md` |
| `gcd(e,phi)=1` | `eth-root` | `eth-root*.md` |
| `d`/`phi` fails `pow`/`p*q` | `factor-from-d`/`rsa-decrypt` | `factor-from-d*.md` |

## The class falsifier

Every bound met → no RSA violation → `class-boundary.md`.

## The record

`knowledge/attempts/` + `negative-results*.md` + `../field-notes.md`.
