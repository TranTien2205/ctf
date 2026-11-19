# Common questions map — the question → the answer file

| Question | The file |
|---|---|
| Which attack? | `attack-table*.md`,`decision-table.md`,`detection-matrix*.md` |
| Is `d` small enough? | `per-bound.md`,`lattice-bounds.md`,`wiener*.md`,`boneh-durfee*.md` |
| How many n's for hastad? | `hastad*.md` — `≥e` coprime |
| What if `gcd(e1,e2)>1`? | `common-modulus*.md` — `m^gcd`, then `nth-root` |
| `fpylll` missing? | `boneh-durfee*.md`,`coppersmith*.md` — pure-python LLL |
| `pow` fails on `m`? | `verify*.md`,`eth-root*.md` — wrong root/decoy |
| `n` prime/square? | `edge-cases*.md`,`boundary-conditions*.md` |
| No violation? | `class-boundary.md`,`negative-results*.md` |
| A leak? | `detection*.md`,`factor-from-d*.md`,`crt*.md` |
| The flags? | `payload-dictionary*.md`,`crypto_attack.py <id> --help` |
| franklin-reiter? | `franklin-reiter*.md` — `tools/crypto/franklin_reiter.py`, manual |

## The honest status

The answers are reads, not guesses — run the bound check first.
