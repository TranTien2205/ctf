# Worked examples variant — the solves, the terse form

## `lcg-recover`

```
x=[15323,22011,4421,9917], m=65536
lcg-recover --outputs 15323,22011,4421 --modulus 65536 → a,c
predict=(a*4421+c)%65536 == 9917 → verified
```

## `lcg-unknown-modulus`

```
o=[o0..o7], m?
lcg-unknown-modulus --outputs o0..o7 → m=2^31 → lcg-recover → a,c → predict
```

## `lcg-truncated` — java

```
nextInt leaks, m=2^48, a=0x5DEECE66D, c=0xB
lcg-truncated --outputs <leaks> --modulus 281474976710656 --a 25214903917 --c 11 --low-bits 16
→ state → key → flag
```

## `berlekamp` + `lfsr`

```
flag{ prefix → keystream bits
berlekamp-massey --bits <bits> → (w,taps)
lfsr-predict --bits --taps --width --count 8*len → keystream → ct⊕ks → flag
```

## `mt19937-clone`

```
625 getrandbits(32) words
mt19937-clone --outputs-file outs.txt --count 1 → predict==o624 → admin id → flag
```

## `xorshift128`

```
4 cookie values
tools/crypto/xorshift128.py --outs o0,o1,o2,o3 --predict 1 → 5th → flag
```

## seed-search

```
token=Random(int(time())).getrandbits(32), iat known
for ts in [iat-5,iat+5]: match → seed → predict → flag
```
