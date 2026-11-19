# Per-bound — every applicability bound → the attack → the falsifier

| The bound | The attack | The falsifier |
|---|---|---|
| `d < n^0.25` | `wiener` | `d ≥ n^0.25` |
| `d < n^0.292` | `boneh-durfee`,`boneh-durfee-escalate` | `d ≥ n^0.292` |
| window `n^0.25` | `coppersmith-high-bits`,`coppersmith-core` | window smaller |
| window `n^(1/e)` | `coppersmith` partial-message | window smaller |
| `m^e < n` | `small-e-root`,`nth-root` | `m^e ≥ n` |
| `≥e` coprime `n`, `∏n>m^e`, no pad | `hastad` | `<e` n's / pad |
| `gcd(e1,e2)=1` | `common-modulus` | `gcd>1` |
| `|p-q|` small | `fermat` | `a` budget passed |
| `p-1` `B`-smooth | `pollard-pm1` | `gcd=1` at `B` |
| shared `p` | `batch-gcd` | all `gcd=1` |
| `a·m1+b` | `franklin-reiter` | not linear |
| `∏pi>m` / `sig`+fault / `dp` consistent | `crt` | `∏pi≤m` / no fault / inconsistent |
| `gcd(e,phi)>1` | `eth-root` | `gcd=1` |
| `d`/`phi`/`p`,`q` held | `factor-from-d`,`rsa-decrypt` | value fails `pow`/`p*q` |

## The rule

The bound is a *theorem* — read it before the attack; a measurement below it
closes the attack.
