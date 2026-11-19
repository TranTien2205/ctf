# Attack catalogue — every implemented attack, the flags, the bound

## Single-modulus

| id | flags | bound | recovers |
|---|---|---|---|
| `fermat` | `--n [--max-iters]` | `|p-q|` small | `p,q` |
| `wiener` | `--n --e` | `d<n^0.25` | `d` |
| `boneh-durfee` | `--n --e [--delta --m --t]` | `d<n^0.292` | `d`/`p,q` |
| `boneh-durfee-escalate` | `--n --e [--m --t]` | `d<n^0.292` | `d`/`p,q` |
| `small-e-root` | `--n --e --c [--max-k]` | `m^e<n` | `m` |
| `nth-root` | `--x --n` | `x=m^n` | `m` |
| `pollard-pm1` | `--n [--b]` | `p-1` `B`-smooth | `p` |
| `coppersmith-high-bits` | `--n --known --bits [--p-bits --m --t]` | window `n^0.25` | `p` |
| `coppersmith-core` | `--n --a --X [--m --t]` | `\|x\|<n^0.25` | `p` |

## Multi-modulus

| id | flags | bound | recovers |
|---|---|---|---|
| `batch-gcd` | `--moduli`/`--file` | a collision | `p` |
| `hastad` | `--pairs`/`--n --c --e` | `≥e` n's | `m` |
| `common-modulus` | `--n --e1 --c1 --e2 --c2` | `gcd(e1,e2)=1` | `m` |
| `crt` | `--residues --moduli` | `∏pi>m` | `m` |

## Terminal

| id | flags | bound | recovers |
|---|---|---|---|
| `factor-from-d` | `--n --e [--d] [--phi]` | the value | `p,q` |
| `rsa-decrypt` | `--n --e --c --p --q` | `p,q` | `m` |
| `eth-root` | `--c --e --factors` | `gcd(e,phi)>1` | `m` |

## Manual (no `crypto_attack.py` id)

`franklin-reiter` → `tools/crypto/franklin_reiter.py` · `crt` Bellcore `gcd` ·
`crt` dp/`dq`/`qInv` loop.
