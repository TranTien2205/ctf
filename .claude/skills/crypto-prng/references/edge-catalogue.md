# Edge catalogue — every non-textbook shape → the handling

## Output-shape edges → handling

| Shape | Handling |
|---|---|
| hex `0x...` | `int(x,16)` |
| base64 | `b64decode` |
| float `0.x` | `int(v*2^53)` or the underlying word pair |
| `x mod n` | reduced model — not `x`, not `x>>b` |
| `x>>b` | `lcg-truncated --low-bits b` |
| `x & mask` | the mask decides the model |
| `randint/choice/shuffle` | post-processed — map to the word |
| `getrandbits(k<32)` | truncated word — low bits dropped |
| a `str()` of an int | `int(v)` |

## Stream-structure edges → handling

| Edge | Handling |
|---|---|
| gaps (other callers) | private oracle / collect every call |
| reseed in window | bound to one contiguous window |
| reseed per request | seed-search, not a stream |
| interleaved endpoints | separate the streams |

## Generator-variant edges → handling

| Variant | Handling |
|---|---|
| `mt_rand`/`mt_srand` (PHP) | PHP MT — different seeding/mode |
| `java.util.Random` | `lcg-truncated --low-bits 16`, `m=2^48` |
| `Math.random` (V8) | `xorshift128+` + double — not `xorshift128` |
| `glibc rand()` | additive feedback — not a plain LCG |
| `numpy/torch` | MT or PCG64 — fingerprint |
| `arc4random`/`SecureRandom` | CSPRNG → out |

## Combined-structure edges → handling

| Edge | Handling |
|---|---|
| LFSR + nonlinear filter | correlation/filter — not plain BM |
| multiple LFSRs combined | `L≈n/2` → correlation per-LFSR |
| `rand()^rand()` | masked — fingerprint first |
| irregular clocking | shrinking — high complexity |

## Seed edges → handling

| Edge | Handling |
|---|---|
| `time()*1000` | ms window — 1000× |
| `pid^time`/`pid+time` | two-factor — bound both |
| `seed=user_id`/counter | small → enumerable |
| `os.urandom`/`secrets` | unbounded → out |

## Verification edges → handling

| Edge | Handling |
|---|---|
| one lucky match | reproduce a SEQUENCE |
| `predict` "close" | bit-for-bit only |
| flag-shaped description | not the recovered object |
| `predict` on training data | use HELD-BACK data |
