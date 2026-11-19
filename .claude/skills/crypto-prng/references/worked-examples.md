# Worked examples — the solves, step by step

## `lcg-recover` worked

```
x = [14234, 99215, 31157], m = 65536
a = (x2-x1)·(x1-x0)^{-1} mod m
  = (31157-99215)·(99215-14234)^{-1} mod 65536
  → a, then c = x1 - a·x0 mod m
crypto_attack.py lcg-recover --outputs 14234,99215,31157 --modulus 65536
→ predict next → match held-back
```

## `lcg-unknown-modulus` worked

```
outs = [o0..o5]
t_i = x_{i+1}-x_i
m = gcd(t1*t0 - t0^2, t2*t1 - t1^2, ...)
→ then lcg-recover
```

## `lcg-truncated` worked

```
leaks = [k>>32 for each]   m, a, c from source
crypto_attack.py lcg-truncated --outputs h... --modulus m --a a --c c --low-bits 32
→ the lattice returns the state → predict
```

## `berlekamp-massey` + `lfsr` worked

```
bits = keystream (>= 2*w)
crypto_attack.py berlekamp-massey --bits ... → (w, taps)
crypto_attack.py lfsr-recover --bits ... --width w → register
crypto_attack.py lfsr-predict --bits ... --taps t --width w --count n → next bits
```

## `mt19937-clone` worked

```
624 consecutive getrandbits(32) outputs
crypto_attack.py mt19937-clone --outputs ... --count 5
→ predict_next == the held-back word
```

## `xorshift128` worked

```
outs = [o0,o1,o2,o3]
python3 tools/crypto/xorshift128.py --outs o0,o1,o2,o3 --predict 3
→ the next 3 outputs
```

## `seed-search` worked

```
token = str(random.seed(int(t))).getrandbits(32)
for ts in range(issue_lo, issue_hi):
    if random.Random(ts).getrandbits(32) == token: seed = ts
```
