# Detection map deep — the full observation→file resolution

## The generator observation → the files

| Observation | Files |
|---|---|
| `LCG`/`a·x+c`/`rand`/mod-m ints | `lcg-*`,`per-attack-lcg-*`,`per-family-lcg*`,`detection*` |
| `LFSR`/taps/bits/`GF(2)` | `lfsr-*`,`per-attack-lfsr-*`,`per-attack-berlekamp*`,`per-family-lfsr*` |
| `mt19937`/`getrandbits`/624 words | `mt-*`,`per-attack-mt19937-clone*`,`per-family-mt-xorshift*` |
| `xorshift`/`x ^= x<<`/4 words | `xorshift-*`,`per-attack-xorshift128*` |
| `seed(time())`/`srand`/`iat` | `seed-*`,`per-family-seed*` |
| `urandom`/`secrets`/`crypto.` | `class-boundary*` — OUT |
| `mt_rand`/`java`/`Math.random`/`drand48` | `real-world-*`,`edge-*` |

## The gate observation → the files

| Observation | Files |
|---|---|
| the count floor | `per-check*`,`boundary*`,`per-boundary` |
| the rawness | `edge-*`,`operator-notes*` |
| the alignment | `edge-*`,`recon-order*` |
| the params | `condition*`,`preconditions*`,`payload-*` |

## The solve observation → the files

| Observation | Files |
|---|---|
| `m` known → `lcg-recover` | `per-attack-lcg-recover*` |
| `m`? → `lcg-unknown-modulus` | `per-attack-lcg-unknown-modulus*` |
| `x>>b`+`a,c,m` → `lcg-truncated` | `per-attack-lcg-truncated*` |
| taps? → `berlekamp`/`lfsr-*` | `per-attack-*` |
| 624 → `mt19937-clone` | `per-attack-mt19937-clone*` |
| 4 → `xorshift128` | `per-attack-xorshift128*` |
| bounded seed | `seed-*` |

## The command observation → the files

| Observation | Files |
|---|---|
| the flags | `payload-*`,`payload-map`,`payload-index` |
| the helpers | `operator-notes*` |
| the cards | `field-manual*`,`quick-reference*` |

## The close observation → the files

| Observation | Files |
|---|---|
| `predict==held` | `verify*`,`evidence*` |
| `flag{` | `evidence*` |
| `predict!=held` | `falsifiers*`,`negative-*`,`troubleshoot*` |
| a kill recorded | `negative-*`,`attempts` |
| the next rung | `decide.py`,`falsifiers*` |
