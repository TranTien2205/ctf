# Boundary cases variant — the edge values, compact

## Count edges

| Attack | At floor | Below |
|---|---|---|
| `lcg-recover` | 3 → `a,c` | 2 → underdet |
| `lcg-unknown-modulus` | 6 → `m` | 5 → no gcd |
| `lcg-truncated` | required → state | <required → underdet |
| `berlekamp` | 2w → `(w,taps)` | 2w-1 → wrong taps |
| `mt19937-clone` | 624 → clone | 623 → NEVER |
| `xorshift128` | 4 → state | 3 → underdet |

## Convention edges

| Flag | Correct | Wrong |
|---|---|---|
| `--low-bits` | `b` dropped | kept → wrong bound |
| `--taps` | 1-indexed-LSB | 0/MSB → mirrored |
| `--outputs` | stream order | sorted → misaligned |

## Shape edges

| Shape | Route |
|---|---|
| `x>>b` | `lcg-truncated` |
| `x mod n` | different model |
| `random()` float | normalize/variant |
| `Math.random` | `xorshift128+` |
| bits | LFSR |

## Seed edges

| Seed | Route |
|---|---|
| `time()` sec | enumerable |
| `time()*1000` ms | 1000× |
| `pid`/`pid^time` | `0..32k`/two-factor |
| `urandom`/`secrets` | OUT |

## Class edges

| Signal | Route |
|---|---|
| `predict!=held` everywhere | reclassify |
| CSPRNG named | out |
