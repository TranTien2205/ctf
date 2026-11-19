# Detection catalogue deep — every signal, the route, the file

## The generator signals → the route → the files

| Signal | Route | Files |
|---|---|---|
| `LCG`/`a·x+c`/`rand()` | `lcg-*` | `per-family-lcg*` |
| `LFSR`/taps/`GF(2)`/shift | `lfsr-*`/`berlekamp` | `per-family-lfsr*` |
| `mt19937`/`getrandbits`/`random` | `mt19937-clone` | `per-family-mt-xorshift*` |
| `xorshift`/`x ^= x<<` | `xorshift128` | `per-attack-xorshift128*` |
| `seed`/`srand`/`mt_srand`/`iat` | seed-search | `per-family-seed*` |
| `urandom`/`secrets`/`SecureRandom` | OUT | `class-boundary*` |
| `mt_rand`/`java`/`Math.random`/`drand48`/`rand` | the variant | `real-world-*`,`edge-*` |

## The count signals → the route → the files

| Signal | Route | Files |
|---|---|---|
| 3 outs | `lcg-recover` | `per-attack-lcg-recover*` |
| 6+ outs | `lcg-unknown-modulus` | `per-attack-lcg-unknown-modulus*` |
| `required` | `lcg-truncated` | `per-attack-lcg-truncated*` |
| 2·w bits | `berlekamp-massey` | `per-attack-berlekamp-massey*` |
| 624 words | `mt19937-clone` | `per-attack-mt19937-clone*` |
| 4 words | `xorshift128` | `per-attack-xorshift128*` |

## The shape signals → the route → the files

| Signal | Route | Files |
|---|---|---|
| `x>>b` high leak | `lcg-truncated` | `per-attack-lcg-truncated*` |
| `x mod n` | different model | `edge-*` |
| taps known | `lfsr-predict` | `per-attack-lfsr-predict*` |
| taps unknown | `berlekamp`/`lfsr-recover` | `per-attack-*` |
| hex/float/`randint` | normalize | `operator-notes*`,`edge-*` |
| bits | LFSR family | `per-family-lfsr*` |
| `Math.random` float | `xorshift128+` | `real-world-*`,`edge-*` |

## The verify signals → the route → the files

| Signal | Route | Files |
|---|---|---|
| `predict==held` | verify + use | `verify*` |
| `predict!=held` | falsify | `falsifiers*`,`negative-*` |
| `flag{`/`CTF{` | record | `evidence*` |
| `gcd→0`/`L≈n/2` | reclassify | `class-boundary*` |
