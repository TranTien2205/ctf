# Field manual — the 15-minute card

## The five reads

```
1. generator (lcg/lfsr/mt/xorshift/seed)
2. count (3/6/required/2w/624/4)
3. raw+consecutive (int, no gap)
4. params (m/a/c/taps/width/low-bits/seed-window)
5. verify (predict==held-back)
```

## The commands

```
lcg-recover --outputs o --modulus m
lcg-unknown-modulus --outputs o
lcg-truncated --outputs h --modulus m --a a --c c --low-bits b
berlekamp-massey --bits b | --keystream-hex | --bits-file
lfsr-predict --bits b --taps t --width w --count n
lfsr-recover --bits b [--taps t] --width w
mt19937-clone --outputs o [--outputs-file f] [--count n]
tools/crypto/xorshift128.py --outs o --predict n
```

## The bounds

```
624 exact · 3/6 lcg · 2w lfsr · 4 xorshift · bounded seed
low-bits = DROPPED · taps = 1-indexed-LSB · outputs = comma ints
```

## The record

```
post-probe → field-notes → classify_solve/attempts → decide.py
```
