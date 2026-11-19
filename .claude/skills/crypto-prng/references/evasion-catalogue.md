# Evasion catalogue — every disguise → what it hides → the response

## Generator-name disguises → response

| Disguise | Hides | Response |
|---|---|---|
| `next()`/`rand()`/`secure_random()` | the real algorithm | read the impl |
| `Random`/`PRNG`/`RNG` class | the algorithm | fingerprint |
| `os.urandom`+`time()` seed | still `time()` | read the seed source |

## Output-shape disguises → response

| Disguise | Hides | Response |
|---|---|---|
| hex/base64/`str` | the raw int | decode |
| `x mod n`/`x&mask` | reduced state | the mod model |
| `x>>b` | truncated | `lcg-truncated --low-bits b` |
| `randint`/`choice`/`shuffle` | post-processed | map to the word |
| `random()`/`uniform` | `2^53` pair | normalize / variant |

## Seed disguises → response

| Disguise | Hides | Response |
|---|---|---|
| `seed(time())`/`int(time())` | the epoch | bound `[issue±slack]` |
| `seed(time()*1000)` | ms | 1000× the window |
| `seed(pid)`/`pid^time` | the range | `0..32k` / two-factor |
| `seed(urandom)`/`secrets` | NOT enumerable | out of class |

## Stream-structure disguises → response

| Disguise | Hides | Response |
|---|---|---|
| shared `random` module | gaps | private oracle |
| reseed per request | not a stream | seed-search |
| interleaved endpoints | gaps | separate streams |

## Platform-variant disguises → response

| Disguise | Hides | Response |
|---|---|---|
| `mt_rand`/`mt_srand` | PHP MT | the PHP variant |
| `java.util.Random` | 48-bit LCG | `lcg-truncated --low-bits 16` |
| `Math.random` | `xorshift128+` | the `+` variant — not `xorshift128` |
| `numpy`/`torch` | MT or PCG64 | fingerprint |
| custom `next()` | LCG/LFSR | fingerprint the structure |

## Verification disguises → response

| Disguise | Hides | Response |
|---|---|---|
| `flag{` in description | not recovered | `predict==held` first |
| one lucky match | not a recovery | reproduce a sequence |
| "looks plausible" | not bit-for-bit | `predict==held` only |
