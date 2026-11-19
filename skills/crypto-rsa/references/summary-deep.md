# Summary deep — crypto-rsa, the whole class

## The one-sentence class

A CTF challenge hands you RSA **numbers** — `n`, `e`, `c`, maybe a leak — and the
answer is a plaintext or private value; every attack is a violation of one of
RSA's six factoring preconditions.

## The decision in one table

| You have | → run |
|---|---|
| ≥2 moduli, same gen | `batch-gcd` |
| same `m`, `e` moduli | `hastad` |
| 1 `n`, 2 `e`, gcd=1 | `common-modulus` |
| `p,q` close | `fermat` |
| `d<n^0.25` | `wiener` |
| `d<n^0.292` | `boneh-durfee` |
| `p`-bits leaked | `coppersmith-*` |
| `e=3`, `m^3<n` | `small-e-root` |
| `p-1` smooth | `pollard-pm1` |
| `d`/`φ`/`p`,`q` | `factor-from-d`/`rsa-decrypt` |
| `m2=a·m1+b` | `franklin_reiter` |
| residues/fault/`dp` | `crt` |
| `gcd(e,φ)>1` | `eth-root` |

## The bounds (the falsifiers)

`d<n^0.25` wiener · `d<n^0.292` boneh-durfee · window≥`n^0.25` coppersmith ·
`m^e<n` small-e · `≥e` n's hastad · `gcd=1` common-modulus · `|p-q|` small fermat
· `B`≥factor pollard · `∏pi>m` crt.

## The verify

`pow(m,e,n)==c` or `p*q==n`. The only proof.

## The honest status

**Catalogue** — no local solve. Published-standard knowledge, not local
experience. `../field-notes.md` grows with real solves.

## The toolchain

`tools/crypto_attack.py <id>` — stdlib-only, pure-python LLL (fpylll absent).
`list` for the inventory + bounds; `<id> --help` for the flags.
