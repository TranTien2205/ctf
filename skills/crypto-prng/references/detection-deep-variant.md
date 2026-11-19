# Detection deep variant — the fingerprint procedures, stepwise

## Procedure 1 — the name read

```
grep -ri 'mt19937|mersenne|xorshift|lfsr|lcg|linear congruential' source/
grep -ri 'getrandbits|randint|random\(|rand\(|mt_rand|srand|seed' source/
grep -ri 'urandom|secrets|crypto\.getrandom|securerandom|arc4random' source/
```

The third grep is the OUT signal — a hit means reclassify.

## Procedure 2 — the shape read

```python
outs = collect()
# bit or word?
assert all(o in (0,1) for o in outs)          # LFSR
assert all(isinstance(o,int) for o in outs)    # LCG/MT/xorshift
assert all(0.0<=o<1.0 for o in outs)           # float — variant
```

## Procedure 3 — the LCG gcd

```python
from math import gcd
from functools import reduce
ts = [outs[i+1]-outs[i] for i in range(len(outs)-1)]
m = reduce(gcd,(ts[i+1]*ts[i-1]-ts[i]*ts[i] for i in range(1,len(ts)-1)))
# m stable+nonzero → LCG with modulus ~m; m→0/1 → not LCG
```

## Procedure 4 — the LFSR BM

```python
# run crypto_attack.py berlekamp-massey --bits <bits>
# L << len(bits)/2 → LFSR of width L; L ≈ len/2 → not
```

## Procedure 5 — the MT clone test

```python
# collect >=624 raw getrandbits(32) words
# crypto_attack.py mt19937-clone --outputs <624>
# predict == word 625 → MT
```

## Procedure 6 — the xorshift test

```python
# tools/crypto/xorshift128.py --outs o0..o3 --predict 1
# predict == o4 → xorshift128; != → variant (128+/64*/rotating)
```

## Procedure 7 — the seed test

```python
for ts in range(iat-slack, iat+slack):
    if Random(ts).<call>() == o0: seed=ts
# a match → seed-search is the attack
```

## The procedure order — cheapest first

```
name → shape → gcd (ints) → BM (bits) → xorshift (4 words) → clone (624)
→ seed-window → none → out
```

## The negative result

No fingerprint matching → `os.urandom`/`secrets`/keyed → record the class
falsifier → reclassify.
