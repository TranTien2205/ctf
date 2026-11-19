# Detection deep — the full fingerprint procedure

## The goal

Name the generator before spending the attack budget. The fingerprint
tests are ordered cheapest-first and each one either routes the solve or
kills a family.

## Step 0 — the source read (free)

```bash
grep -rniE 'mt19937|mersenne|xorshift|lfsr|shift.?register|lcg|linear.?congruential' .
grep -rniE 'getrandbits|randint|random\(|rand\(|mt_rand|srand|seed|nextInt|rand48' .
grep -rniE 'urandom|secrets\.|crypto\.get|securerandom|arc4random|hmac|sha256' .
```

- First grep hits → the family named. Route.
- Third grep hits → `urandom`/`secrets`/CSPRNG/keyed → **wrong class**,
  reclassify to `crypto-symmetric-oracle`.

## Step 1 — the shape read (free)

```python
outs = collect_outputs()
if all(o in (0,1) for o in outs):            family = 'lfsr'
elif all(isinstance(o,int) and o < 2**32 for o in outs): family = 'word-gen'
elif all(0.0 <= o < 1.0 for o in outs):      family = 'float-gen'
elif all(isinstance(o,int) for o in outs):   family = 'int-gen'
```

- `bits` → LFSR branch.
- `word-gen`/`int-gen` → LCG/MT/xorshift branch.
- `float-gen` → `random()`/`Math.random` variant branch.

## Step 2 — the LCG gcd (cheap, ints only)

```python
from math import gcd
from functools import reduce
ts = [outs[i+1]-outs[i] for i in range(len(outs)-1)]
m = reduce(gcd, (ts[i+1]*ts[i-1]-ts[i]*ts[i] for i in range(1,len(ts)-1)), 0)
# abs(m) nonzero and stable → LCG; 0/1 → not affine
```

## Step 3 — the BM complexity (cheap, bits only)

```bash
python3 tools/crypto_attack.py berlekamp-massey --bits <bits>
```

- `L` convergent & « n → LFSR of width `L`.
- `L ≈ n/2` → combiner or non-LFSR.

## Step 4 — the count discriminator (word-gen)

- ≥624 raw `getrandbits(32)` words → `mt19937-clone` is feasible.
- 4-623 → `xorshift128` or seed-search.
- `<4` → collect more.

## Step 5 — the seed read (cheap)

`seed=`/`srand`/`mt_srand`/`init`/`iat`/`created`/`pid` in source or the
artifact → bound the window → seed-search is live.

## Step 6 — the decisive test

The clone/inversion itself: `mt19937-clone`/`xorshift128` — `predict ==
held` is the fingerprint AND the recovery.

## The decision

| Result | Route |
|---|---|
| name + shape + count → family | the matching `per-attack-*` |
| gcd stable `m` | `lcg-recover`/`lcg-unknown-modulus` |
| BM `L` small | `lfsr-*` |
| 624 + clone works | `mt19937-clone` |
| 4 + invert works | `xorshift128` |
| bounded seed | seed-search |
| none | CSPRNG/keyed → out |
