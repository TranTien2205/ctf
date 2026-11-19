# Detection catalogue — signal → route → files

## The generator signals → routes → files

| Signal | Route | Files |
|---|---|---|
| `LCG`/`x_{i+1}=a·x+c` | `lcg-*` | `per-family-lcg.md` |
| `LFSR`/taps/GF(2) | `lfsr-*` | `per-family-lfsr.md` |
| `mt19937`/`getrandbits` | `mt19937-clone` | `per-family-mt-xorshift.md` |
| `x ^= x<<13` | `xorshift128` | `per-family-mt-xorshift.md` |
| `seed(time())`/`srand` | seed-search | `per-family-seed.md` |
| token/nonce "random" | fingerprint | `detection-deep.md` |

## The count signals → routes → files

| Signal | Route | Files |
|---|---|---|
| 3 outs | `lcg-recover` | `per-attack-lcg-recover.md` |
| 6+ outs | `lcg-unknown-modulus` | `per-attack-lcg-unknown-modulus.md` |
| 2·w bits | `berlekamp-massey` | `per-attack-berlekamp-massey.md` |
| 624 words | `mt19937-clone` | `per-attack-mt19937-clone.md` |
| 4 words | `xorshift128` | `per-attack-xorshift128.md` |

## The shape signals → routes → files

| Signal | Route | Files |
|---|---|---|
| high bits only | `lcg-truncated` | `per-attack-lcg-truncated.md` |
| taps known | `lfsr-predict` | `per-attack-lfsr-predict.md` |
| taps unknown | `berlekamp-massey`/`lfsr-recover` | `per-attack-*.md` |
| hex/float/mod | normalize | `edge-cases*.md` |

## The close signals → routes → files

| Signal | Route | Files |
|---|---|---|
| `predict==held` | verify | `verify*.md` |
| `predict!=held` | falsify | `falsifiers*.md` |
| `flag{` | record | `evidence*.md` |
