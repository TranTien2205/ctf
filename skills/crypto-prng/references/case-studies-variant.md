# Case studies variant — the solves, compact

## The LCG token

`GET /token` ints → `m` in source → `lcg-recover` → `predict==held` →
forge → flag.

## The unknown-mod `rand()`

6 outs → `lcg-unknown-modulus` → `m=2^31` → `lcg-recover` → `a,c` →
predict.

## The `java.util.Random` keygen

`nextInt` leaks `x>>16` → `lcg-truncated --low-bits 16` → state → key →
flag.

## The LFSR stream

`flag{` prefix → keystream → `berlekamp-massey` → `lfsr-predict` →
`ct⊕ks` → flag.

## The MT session

625 `getrandbits(32)` → `mt19937-clone` → `predict==o624` → admin id →
flag.

## The timestamp seed

`token=random.seed(int(t))`, `iat` → window → enumerate → seed → predict
→ flag.

## The xorshift cookie

4 cookies → `xorshift128 --outs --predict` → 5th → flag.

## The pattern

fingerprint → count → the matching attack → `predict==held` → use →
flag — the discriminator is the param-known count.
