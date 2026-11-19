# Detection catalogue variant — the signals, compact

## Generator signals

| Signal | Route |
|---|---|
| `LCG`/`a·x+c`/`lcg` | `lcg-*` |
| `LFSR`/taps/`GF(2)`/`shift` | `lfsr-*`/`berlekamp` |
| `mt19937`/`getrandbits`/`random` | `mt19937-clone` |
| `xorshift`/`x ^= x<<` | `xorshift128` |
| `seed(time())`/`srand`/`mt_srand` | seed-search |
| `urandom`/`secrets`/`SecureRandom` | OUT |
| `mt_rand`/`java.util.Random`/`Math.random` | the variant |

## Count signals

| Count | Attack |
|---|---|
| 3 | `lcg-recover` |
| 6+ | `lcg-unknown-modulus` |
| ~required | `lcg-truncated` |
| 2w bits | `berlekamp` |
| 624 | `mt19937-clone` |
| 4 | `xorshift128` |

## Shape signals

| Shape | Route |
|---|---|
| raw ints | direct |
| `x>>b` | `lcg-truncated` |
| `x mod n` | different model |
| floats | `×2^53` pair / variant |
| bits | LFSR |
| hex/b64 | decode |

## Verify signals

| Signal | Meaning |
|---|---|
| `predict==held` | recovered — proceed to flag |
| `predict!=held` | falsified — record + decide.py |
| `flag{`/`CTF{` | impact — post-probe/pre-flag |
