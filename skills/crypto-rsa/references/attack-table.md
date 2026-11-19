# Attack table — every RSA attack id, its trigger, its bound

The applicability text below is what `tools/crypto_attack.py list` prints —
reproduce the bound before running, because exceeding it is the class falsifier.

| Attack id | Hold | Bound / falsifier | Output |
|---|---|---|---|
| `batch-gcd` | ≥2 moduli, same bad RNG | needs a shared prime; single `n` never applies | shared `p`, then `q`, `d`, `m` |
| `common-modulus` | one `n`, `c1`,`c2`, `e1`,`e2` | `gcd(e1,e2)==1`; shares a factor → dead | `m` via Bezout `a*e1+b*e2=1` |
| `coppersmith-high-bits` | `n`, `e`, `c`, top half of `p` | known window ≥ `n^0.25` | `p` → `d` → `m` |
| `coppersmith-core` | centred guess `a` of a factor | `|p-a| < n^0.25`-ish window | `p` → `d` → `m` |
| `eth-root` / `small-e-root` | one `n`, small `e`, short `m` | only if `m^e < n` (no wrap) | `m` by exact root |
| `factor-from-d` | `n`, `e`, `d` (or `phi`) | none — direct | `(p,q)` → `m` |
| `fermat` | `n` with `p≈q` | gap must be small; distant `p,q` → dead | `p`,`q` → `d` → `m` |
| `franklin_reiter` | `c1`,`c2` of `m`,`a*m+b` mod `n` | linear relation required | `m` |
| `hastad` | `e` ciphertexts of one `m`, `e` moduli | need ≥ `e` recipients; fewer → pad/coppersmith | `m` via CRT + root |
| `nth-root` | `m^e` with no wrap | exact root must land | `m` |
| `pollard-pm1` | `n` with `p-1` smooth | only helps when `p-1` is smooth | `p` → `d` → `m` |
| `rsa-decrypt` | factor/`d`/`phi` held | terminal step | `m` |
| `wiener` | `n`, `e` with `d < n^0.25` | `d` above `0.25` bound → use boneh-durfee | `d` → `m` |
| `boneh-durfee` | `n`, `e`, `d < n^0.29` | lattice bound ~`0.292`; above → dead | `d` → `m` |
| `boneh-durfee-escalate` | same, no manual `m` param | auto-escalates the lattice `m` | `d` → `m` |
| `crt` | residues of `m` mod small primes | product of moduli > `m` needed | `m` |

## The chain

Every attack ends the same way: recover `(p,q)` or `d` or `phi`, then
`rsa-decrypt` to `m`, then **verify** `pow(m,e,n)==c`. A plaintext that fails
`pow` is a candidate, not a recovery.
