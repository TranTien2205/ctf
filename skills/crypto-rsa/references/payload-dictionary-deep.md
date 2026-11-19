# Payload dictionary deep — the invocations, with the flags explained

## The shape

`python3 tools/crypto_attack.py <id> <flags>` — every id also takes `--json`
(compact output) and `--in <file>` (a JSON object with the params, `-` for
stdin). `<id> --help` shows the exact flags.

## The single-modulus ids

| id | The flags | The bound |
|---|---|---|
| `fermat` | `--n <n> [--max-iters <K>]` | `|p-q|` small |
| `wiener` | `--n <n> --e <e>` | `d < n^0.25` |
| `boneh-durfee` | `--n --e [--delta] [--m] [--t]` | `d < n^0.292` |
| `boneh-durfee-escalate` | `--n --e [--m] [--t]` | `d < n^0.292`, params up |
| `small-e-root` | `--n --e --c [--max-k]` | `m^e < n` |
| `nth-root` | `--x <x> --n <n>` | `x = m^n` exact |
| `pollard-pm1` | `--n [--b <B>]` | `p-1` `B`-smooth |
| `coppersmith-high-bits` | `--n --known <a> --bits <b> [--p-bits] [--m] [--t]` | window `n^0.25` |
| `coppersmith-core` | `--n --a <a> --X <bound> [--m] [--t]` | `\|x\| < n^0.25` |

## The multi-modulus ids

| id | The flags | The bound |
|---|---|---|
| `batch-gcd` | `--moduli n1 n2 ...` / `--file` | a collision |
| `hastad` | `--pairs "n1,c1;n2,c2" --e <e>` / `--n --c` | `≥e` n's |
| `common-modulus` | `--n --e1 --c1 --e2 --c2` | `gcd(e1,e2)=1` |
| `crt` | `--residues "r1,r2" --moduli "p1,p2"` | `∏pi>m` |

## The terminal ids

| id | The flags | The bound |
|---|---|---|
| `factor-from-d` | `--n --e [--d] [--phi]` | the value held |
| `rsa-decrypt` | `--n --e --c --p --q` | the factors held |
| `eth-root` | `--c --e --factors "<p>,<q>"` | `gcd(e,phi)>1` |

## Not a `crypto_attack.py` id

`franklin-reiter` is `tools/crypto/franklin_reiter.py` — a standalone module —
run it or the manual poly-`gcd`. The Bellcore `sig`/`sig-faulty` split and the
`dp`/`dq`/`qInv` recovery are manual `gcd`/loop techniques — no `crypto_attack.py`
flag.
