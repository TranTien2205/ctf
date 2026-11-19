# Boundary catalogue — every boundary, the value, the consequence

## Count boundaries → consequence

| Boundary | Value | At | Below |
|---|---|---|---|
| `lcg-recover` | 3 | `a`,`c` | underdetermined |
| `lcg-unknown-modulus` | 6 | `m` | gcd unpinned |
| `lcg-truncated` | required | state | lattice under-det |
| `berlekamp-massey` | 2w | `(w,taps)` | wrong taps |
| `lfsr-*` | w/2w | register | under-det |
| `mt19937-clone` | 624 | clone | NEVER |
| `xorshift128` | 4 | state | under-det |
| seed-search | window | seed | unbounded→out |

## Convention boundaries → consequence

| Boundary | Correct | Wrong |
|---|---|---|
| `--low-bits` | DROPPED `b` | kept count → wrong bound |
| `--taps` | 1-indexed-LSB | 0/MSB → mirrored poly |
| `--outputs` | stream order | sorted/dedup → misaligned |
| MT word | `getrandbits(32)` | `random()`/`randint` → wrong |

## Shape boundaries → consequence

| Shape | Route | Wrong route |
|---|---|---|
| `x>>b` | `lcg-truncated` | `lcg-recover` → wrong a,c |
| `x mod n` | different model | `lcg-*` → wrong |
| float `random()` | normalize/variant | `mt19937-clone` → garbage |
| bits | LFSR family | `lcg-*` → wrong |
| `Math.random` | `xorshift128+` | `xorshift128` → wrong state |

## Seed boundaries → consequence

| Seed | Window | Route |
|---|---|---|
| `int(time())` sec | `±slack` | seed-search |
| `time()*1000` ms | `±slack*1000` | seed-search (bigger) |
| `pid` | `0..32k` | seed-search |
| `pid^time` | bound both | two-factor enumerate |
| `os.urandom` | unbounded | OUT |

## Class boundaries → consequence

| Signal | Class | Route |
|---|---|---|
| `urandom`/`secrets` | CSPRNG | out |
| `AES`/`HMAC`/keyed | symmetric-oracle | reclassify |
| decode→structure | encoding-carrier | reclassify |
| `k`/`r`,`s`/ECDSA | ecc-dlog | reclassify |
| `predict!=held` everywhere | wrong class | reclassify |
