# Evasion map — disguise → the read → the files

## The name disguises → the files

| Disguise | Read | Files |
|---|---|---|
| `next()`/`rand()`/`secure_random()` | the impl | `evasion*`,`detection*` |
| `Random`/`PRNG`/`RNG` | the algorithm | `detection*` |
| `os.urandom`+time seed | still `time()` | `per-family-seed*` |

## The output disguises → the files

| Disguise | Read | Files |
|---|---|---|
| hex/base64/`str` | decode | `operator-notes*`,`edge-*` |
| `x mod n`/`x&mask` | reduced | `edge-*`,`boundary-*` |
| `x>>b` | truncated | `per-attack-lcg-truncated*` |
| `randint`/`choice`/`shuffle` | post-processed | `edge-*` |
| `random()`/`Math.random` | float/variant | `edge-*`,`real-world-*` |

## The seed disguises → the files

| Disguise | Read | Files |
|---|---|---|
| `time()`/`int(time())` | epoch | `per-family-seed*` |
| `time()*1000` | ms | `per-family-seed*` |
| `pid`/`pid^time` | range/two-factor | `per-family-seed*` |
| `urandom`/`secrets` | unbounded → out | `class-boundary*` |

## The stream disguises → the files

| Disguise | Read | Files |
|---|---|---|
| shared `random` | gaps | `edge-*`,`recon-order*` |
| reseed per request | not a stream | `per-family-seed*` |
| interleaved | separate | `edge-*` |

## The variant disguises → the files

| Disguise | Read | Files |
|---|---|---|
| `mt_rand`/`mt_srand` | PHP MT | `real-world-*`,`edge-*` |
| `java.util.Random` | 48-bit LCG | `per-attack-lcg-truncated*` |
| `Math.random` | `xorshift128+` | `real-world-*`,`edge-*` |
| `numpy`/`torch` | MT/PCG64 | `edge-*` |
| custom `next()` | LCG/LFSR | `detection*` |
