# Troubleshoot deep — `predict != held`, by attack

## The universal ladder

```
predict != held
  → the convention? (low-bits / taps / modulus / outputs order)
  → the variant? (mt_rand / xorshift+ / java.util.Random / glibc rand)
  → the normalization? (hex / float / mod / randint)
  → the alignment? (gap / reseed in the window)
  → the count? (under the floor)
  → still fail → the model is wrong → reclassify → falsifier → attempts
```

## `lcg-recover` fails

| Symptom | Likely cause | Fix |
|---|---|---|
| `gcd(x1-x0,m)!=1` | even diff on power-of-2 m | gather an odd difference / factor `m` |
| `a,c` wrong | `x mod n`/float inputs | normalize to raw `x` |
| `predict!=held` | wrong `m` | re-derive `m` (2^31 vs 2^32 vs 2^48) |
| `predict!=held` | non-consecutive | re-collect a contiguous window |

## `lcg-unknown-modulus` fails

| Symptom | Likely cause | Fix |
|---|---|---|
| gcd = 0/1 | not affine / gap | re-fingerprint, check consecutiveness |
| gcd = multiple of m | shared factor | divide by small factors / more outputs |
| gcd = a factor of m | composite m | factor the gcd, test candidates |
| `lcg-recover` fails after | wrong `m` | re-check the gcd's factors |
| `predict!=held` | not an LCG | re-fingerprint — LFSR/MT/xorshift |

## `lcg-truncated` fails

| Symptom | Likely cause | Fix |
|---|---|---|
| no short vector | `low-bits` wrong | recount the DROPPED bits |
| `predict!=held` | `a`/`c`/`m` wrong | re-derive from source |
| `predict!=held` | leak isn't `x>>b` | it's `x mod n`/`x&mask` — different model |
| under-determined | too few `h_i` | collect to `required`+ |

## `berlekamp-massey` / `lfsr-*` fails

| Symptom | Likely cause | Fix |
|---|---|---|
| `L ≈ n/2` | not a plain LFSR | combiner → correlation attack |
| `predict` diverges | taps convention | re-index (1-LSB vs 0 vs MSB) |
| `predict` diverges | bit order | flip per-byte bit order |
| `predict` diverges | width wrong | re-derive `w` from BM's `L` |
| all-zeros output | degenerate register | wrong width / a zero state |

## `mt19937-clone` fails

| Symptom | Likely cause | Fix |
|---|---|---|
| <624 | the gate | collect more / seed-search |
| `predict!=held` | floats/randint inputs | collect raw `getrandbits(32)` |
| `predict!=held` | non-consecutive | shared `random` — collect every call |
| `predict!=held` | reseed in window | bound to one contiguous window |
| `predict!=held` | `mt_rand`/variant | PHP MT differs — fingerprint the variant |

## `xorshift128` fails

| Symptom | Likely cause | Fix |
|---|---|---|
| `predict!=held` | `xorshift128+`/64*/rotating | fingerprint the variant |
| `predict!=held` | `Math.random` doubles | the `+` variant + float — different tool |
| `predict!=held` | non-consecutive | collect a contiguous 4-tuple |
| <4 outs | the gate | collect more |

## seed-search fails

| Symptom | Likely cause | Fix |
|---|---|---|
| no seed matches | window too narrow | widen `[issue-slack, now]` |
| no seed matches | wrong call | reproduce the SAME call (randint vs getrandbits) |
| no seed matches | wrong generator | `mt_rand`/`java.util.Random`/`rand` differ |
| window too big | ms/ns units | bound tighter or it's CSPRNG → wrong class |
