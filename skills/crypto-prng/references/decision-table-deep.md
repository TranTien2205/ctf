# Decision table deep — the full branch matrix

## The observation × parameter matrix

| Observation | Params | Count | Attack | Verify |
|---|---|---|---|---|
| raw ints, `x_{i+1}=a·x+c` | `m` | 3 | `lcg-recover` | `predict==held` |
| raw ints, `x_{i+1}=a·x+c` | none | 6 | `lcg-unknown-modulus` | `predict==held` |
| `x>>b` leaks | `a`,`c`,`m` | required | `lcg-truncated` | `predict==held` |
| bitstream | none | 2w | `berlekamp-massey` | BM→predict |
| bitstream | `taps`+`w` | ≥w | `lfsr-predict` | `predict==held` |
| bitstream | `w` | ≥2w | `lfsr-recover` | predict |
| 32-bit words | none | 624 | `mt19937-clone` | `predict==held` |
| 32-bit words | none | 4 | `xorshift128` | `predict==held` |
| any + `seed=f(small)` | bounded window | window | seed-search | `seed→o0,o1` |

## The "known" column — the discriminator

The single deciding question for LCG: **what's known?** `m` → `recover`;
nothing → `unknown-modulus`; `a`,`c`,`m` → `truncated`. For LFSR: **taps
known?** → `predict`; else → `berlekamp-massey`/`recover`.

## The count column — the gate

The second deciding question: **how many outputs?** Below the floor the
attack can't run — collect more or switch family. 624 is the hard MT
gate; 3/6/`required`/`2w`/`4` the others.

## The shape column — the normalizer

The third deciding question: **raw or post-processed?** `x>>b` →
truncated; `x mod n` → a different model; float/hex/`randint` →
normalize; bits → LFSR; words → MT/xorshift.

## The trap rows

| Observation | Trap | Real route |
|---|---|---|
| `Math.random` floats | `xorshift128` | `xorshift128+` — different tool |
| `java.util.Random.nextInt` | `lcg-unknown-modulus` | `lcg-truncated --low-bits 16` |
| `glibc rand()` | `lcg-recover` | additive — different recurrence |
| `random.seed(time())` | `mt19937-clone` | seed-search |
| `os.urandom` | any | out of class |
| `rand()^rand()` | `lcg-recover` | combined — masked |

## The verify column — universal

`predict == held-back` — the one accept across every row.
