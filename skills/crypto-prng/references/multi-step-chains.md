# Multi-step chains — the composed attacks

## The `lcg → token` chain

```
service emits tokens → collect 3+ → lcg-recover (m known) → a,c
→ predict next token → forge/admin → flag
```

## The `lfsr → keystream → decrypt` chain

```
ct + keystream bits → berlekamp-massey → lfsr-recover
→ lfsr-predict --count n → keystream → xor ct → flag
```

## The `mt → session` chain

```
session ids from random.getrandbits(32) → collect 624 → mt19937-clone
→ predict_next → next session id → hijack → flag
```

## The `seed → forge` chain

```
token = f(seed(time())) → bound epoch → random.seed(ts) match
→ predict → forge → flag
```

## The `truncated-lcg → state → flag` chain

```
leaked high bits ×N → lcg-truncated --low-bits b → state → predict → flag
```

## The `unknown-m → m → a,c → token` chain

```
outs ×6+ → lcg-unknown-modulus → m → lcg-recover → a,c → predict → flag
```

## The boundary

Crypto step → flag step — the predicted output is `class` evidence; the
flag in the forged/decrypted bytes is `impact`. Both belong to the chain.
