# Detection summary — the one-screen card

## The reads

```
generator?   lcg / lfsr / mt19937 / xorshift128 / seed / CSPRNG(out)
count?       3 / 6 / req / 2w / 624 / 4 / window
raw?         ints, consecutive, no gaps, no reseed
params?      m | a,c | taps,width | low-bits | seed window
```

## The commands

```
lcg-recover --outputs --modulus        lcg-unknown-modulus --outputs
lcg-truncated --outputs --modulus --a --c --low-bits
berlekamp-massey --bits|--keystream-hex|--bits-file
lfsr-recover --bits [--taps] --width   lfsr-predict --bits --taps --width --count
mt19937-clone --outputs|--outputs-file [--count]
tools/crypto/xorshift128.py --outs --predict
```

## The traps

```
low-bits=DROPPED · taps=1-indexed-LSB · raw ints only · Math.random=128+
624/2w/3/6/4 are hard floors
```

## The verify

`predict == held-back` — the only accept.
