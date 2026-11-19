# Field manual deep — the 15-minute card, annotated

## The five reads — expanded

```
1. generator   lcg | lfsr | mt19937 | xorshift128 | seed(time/pid) | CSPRNG(out)
2. count       3 | 6 | required | 2w | 624 | 4 | window-size
3. raw+consec  ints (not hex/float/mod/randint) AND no gaps AND no reseed
4. params      m | a,c | taps,width | low-bits(=dropped) | seed window
5. verify      predict_next == held_back  (bit-for-bit, never skip)
```

## The commands — expanded

```bash
# LCG — m known / unknown / truncated
crypto_attack.py lcg-recover --outputs o --modulus m
crypto_attack.py lcg-unknown-modulus --outputs o
crypto_attack.py lcg-truncated --outputs h --modulus m --a a --c c --low-bits b
# LFSR — taps unknown / state / predict
crypto_attack.py berlekamp-massey --bits b | --keystream-hex h | --bits-file f
crypto_attack.py lfsr-recover --bits b [--taps t] --width w
crypto_attack.py lfsr-predict --bits b --taps t --width w --count n
# MT / xorshift
crypto_attack.py mt19937-clone --outputs o | --outputs-file f [--count n]
tools/crypto/xorshift128.py --outs o --predict n [--selftest]
# seed — manual enumeration, no attack id
```

## The bounds — expanded

```
counts:  624 exact | 3/6 lcg | 2w lfsr | 4 xorshift | bounded seed
conventions: low-bits=DROPPED | taps=1-indexed-LSB | outputs=comma ints
             --count=next-outputs | --outs/--bits/--outputs variants
shapes:    raw words only — float/mod/randint normalize first
variants:  mt_rand | xorshift128+ | java.util.Random | glibc rand
```

## The fingerprint — expanded

```
gen named? → skip to count
gcd(t_{i+1}t_{i-1}-t_i^2) → affine → LCG
berlekamp-massey L << n/2 → LFSR   L ≈ n/2 → combiner/none
624 raw words → mt19937-clone test
os.urandom/secrets → CSPRNG → out
```

## The record — expanded

```
post-probe --verdict confirms --evidence 'predict==held' --response <bytes>
pre-flag --value 'flag{...}' --evidence '<bytes>'
field-notes → classify_solve | attempts (falsifier + reopen_if) → decide.py
```

## The honest status — expanded

Catalogue class — no local chain cards. The corpus is standard mechanism
+ field procedure. `predict==held` is the only proof a state is real.
