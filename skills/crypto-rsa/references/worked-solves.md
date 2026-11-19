# Worked solves — complete end-to-end walkthroughs

## Solve 1 — `q=next_prime(p)` → `fermat`

```python
# chal.py
p = getPrime(512)
q = next_prime(p)          # the tell: primes adjacent
n = p * q
e = 65537
c = pow(m, e, n)
# given: n, e, c
```

The discriminator: the keygen says `next_prime` — primes are close, `|p-q|`
is a few hundred at most.

```python
from sympy import integer_nthroot, isqrt
a = isqrt(n) + 1
for i in range(1_000_000):
    b2 = a*a - n
    b, ok = integer_nthroot(b2, 2)
    if ok:
        p, q = a+b, a-b
        break
    a += 1
assert p*q == n                      # the factor gate
phi = (p-1)*(q-1)
d = pow(e, -1, phi)
m = pow(c, d, n)
assert pow(m, e, n) == c            # the plaintext gate
from Crypto.Util.number import long_to_bytes
print(long_to_bytes(m))              # the flag bytes
```

Or: `crypto_attack.py fermat --n <n> --max-iters 1000000` → `p`,`q` →
`rsa-decrypt --n --e --c --p --q`.

## Solve 2 — `e=3`, `m³<n` → `small-e-root`

```python
# chal.py
e = 3
m = bytes_to_long(b"flag{short}")
c = pow(m, 3, n)     # m³ < n → c = m³ exactly
# given: n, e, c
```

`m` is 11 bytes ≈ 88 bits; `m³` ≈ 264 bits < `n` (2048 bits) → `c = m³`.

```python
from sympy import integer_nthroot
m, exact = integer_nthroot(c, 3)
assert exact and pow(m, 3) == c      # no mod n — the wrap never engaged
print(long_to_bytes(m))              # flag{short}
```

Or: `crypto_attack.py small-e-root --n <n> --e 3 --c <c>`.

## Solve 3 — `e`≈`n`, `d` small → `wiener`

```python
# chal.py
d = getPrime(64)          # small d — 'fast decryption'
e = inverse(d, phi)       # e ≈ n in bit-length — the tell
c = pow(m, e, n)
```

`e` is ~2048 bits ≈ `n` — small `d` in disguise. `d=64-bit < n^0.25=512-bit` →
Wiener.

```bash
crypto_attack.py wiener --n <n> --e <e>     # → d
```

```python
m = pow(c, d, n)
assert pow(m, e, n) == c
```

## Solve 4 — a `.json` of `n` → `batch-gcd`

```python
# output.json — 50 moduli from a weak keygen
ns = [n1, n2, ..., n50]
```

```bash
crypto_attack.py batch-gcd --moduli n1 n2 ...   # or --file keys.json
# → (i, j, p) — a collision
```

```python
p = g; q = ns[i]//p
assert p*q == ns[i]
phi = (p-1)*(q-1); d = pow(e,-1,phi); m = pow(c,d,ns[i])
assert pow(m,e,ns[i]) == c
```

## Solve 5 — broadcast `m`, `e=3`, 3 n's → `hastad`

```python
# chal.py — the same m to 3 recipients
for i in range(3):
    c_i = pow(m, 3, n_i)
# given: n1,n2,n3, c1,c2,c3, e=3
```

```bash
crypto_attack.py hastad --pairs "n1,c1;n2,c2;n3,c3" --e 3   # → m
```

```python
from sympy.ntheory.modular import crt
from sympy import integer_nthroot
x = crt([n1,n2,n3],[c1,c2,c3])[0]
m, ok = integer_nthroot(x, 3); assert pow(m,3)==x
```

## Solve 6 — `p` high bits leaked → `coppersmith`

```python
# leak: p_high = top 256 bits of p (of 512)
a = p_high << 256
```

```bash
crypto_attack.py coppersmith-high-bits --n <n> --known <a> --bits 256
# → x;  p = a+x
```

## Solve 7 — `d` held → `factor-from-d` → `rsa-decrypt`

```bash
crypto_attack.py factor-from-d --n <n> --e <e> --d <d>   # → p,q
crypto_attack.py rsa-decrypt --n <n> --e <e> --c <c> --p <p> --q <q>
```

## Solve 8 — `gcd(e,phi)=2` → `eth-root`

```bash
crypto_attack.py eth-root --c <c> --e <e> --factors "<p>,<q>"   # → the g candidates
```

`pow(m_i,e,n)==c` + the flag format picks the true `m`.

## The verify, always

`pow(m,e,n)==c` / `p*q==n` — run them.
