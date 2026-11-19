# Quick reference deep — the card with the reasoning

## The generators — with the why

```
lcg:        x_{i+1}=a·x_i+c mod m — affine → telescope kills m, a,c
lfsr:       shift+xor(taps), w bits — linear GF(2) → 2w bits pin it
mt19937:    624-word state, invertible temper → 624 words = the state
xorshift128: x^(x<<11)/rotate, w output — linear GF(2) → 4 words = state
seed:       state_0=init(seed) — bounded seed → enumerate
```

## The floors — with the why

```
3   lcg-recover   — a,c = 2 unknowns, need 3 pts
6   lcg-unknown-modulus — add m, need 6 for the gcd
req lcg-truncated — lattice needs enough h_i
2w  berlekamp-massey — w bits state + w to pin taps
624 mt19937-clone — 19968/32 exactly
4   xorshift128 — 128/32 exactly
win seed-search — |seed| tries
```

## The commands — with the flag note

```
lcg-recover --outputs o --modulus m          # m required
lcg-unknown-modulus --outputs o              # NO --modulus
lcg-truncated --outputs h --modulus m --a a --c c --low-bits b  # all req
berlekamp-massey --bits b|--keystream-hex|--bits-file  # one form
lfsr-recover --bits b [--taps t] --width w   # taps optional
lfsr-predict --bits b --taps t --width w --count n     # taps+width req
mt19937-clone --outputs o|--outputs-file f [--count n]
tools/crypto/xorshift128.py --outs o --predict n       # standalone
```

## The traps — the top five

```
1. --low-bits = DROPPED (not kept)      # the #1 operator error
2. --taps = 1-indexed-LSB               # wrong convention → diverge
3. outputs must be RAW ints             # float/mod/randint → wrong
4. Math.random = xorshift128+ NOT 128   # wrong variant
5. 624 exact — 623 never clones         # the hard gate
```

## The verify — the one rule

```
predict_next == held_back — bit-for-bit, on data the attack never saw
```
