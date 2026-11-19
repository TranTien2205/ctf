# Worked examples deep — the annotated solves

## `fermat` — `q=next_prime(p)`

```python
# n = p*q where q = next_prime(p) — p and q differ by ~hundreds
a = isqrt(n) + 1
while True:
    b2 = a*a - n
    if is_square(b2): p, q = a+isqrt(b2), a-isqrt(b2); break
    a += 1
# p*q == n → phi → d → m → pow(m,e,n)==c
```

The `a` climb lands in `O(|p-q|)` steps — a few hundred for adjacent primes.

## `wiener` — `d` small, `e`≈`n`

```python
# e/n has convergents k/d; d < n^0.25 → d is a convergent
for (k,d) in convergents(e/n):
    if (e*d-1) % k == 0:
        phi = (e*d-1)//k
        s = n - phi + 1                    # p+q
        if discriminant s²-4n is square:   # p,q = (s±√disc)/2
            return d, p, q
# → d → m = pow(c,d,n) → pow(m,e,n)==c
```

## `boneh-durfee` — `d` in `n^0.25..n^0.292`

```python
# f(x,y) = x(A-y)+1 mod e, A=n+1 — root (k,s), s=p+q
# LLL → the small roots → d=k, p,q from s
```

## `batch-gcd` — a shared `p`

```python
for i,j in pairs(ns):
    g = gcd(ns[i], ns[j])
    if g > 1: p = g; qi, qj = ns[i]//p, ns[j]//p
```

## `small-e-root` — `m³<n`

```python
m, exact = integer_nthroot(c, 3)
assert exact and pow(m,3) == c     # no mod n — c was m³ plain
```

## `hastad` — `e` n's, same `m`

```python
x = crt(ns, cs)[0]                 # x = m^e mod ∏ni = m^e exactly
m, ok = integer_nthroot(x, e); assert pow(m,e)==x
```

## `common-modulus` — `gcd(e1,e2)=1`

```python
g,a,b = gcdex(e1,e2); m = pow(c1,a,n)*pow(c2,b,n) % n
assert pow(m,e1,n)==c1
```

## `pollard-pm1` — `p-1` smooth

```python
a = 2
for j in range(2,B+1): a = pow(a,j,n)
g = gcd(a-1,n)                     # = p
```

## `coppersmith` — `p` bits

```python
# f(x) = a+x ≡ 0 mod p — LLL small root → x → p = a+x
```

## `franklin-reiter` — `m2=a·m1+b`

```python
# gcd(x^e-c1, (a*x+b)^e-c2) over Z_n[x] = x-m
```

## `crt` — residues / Bellcore / dp

```python
# residues: x = crt(pi, ri)[0] → m (if ∏pi>m)
# Bellcore: gcd(pow(sig_faulty,e,n)-m, n) → q
# dp: for k in 1..e: p=(e*dp-1)/k+1; if n%p==0 → p
```

## `factor-from-d`/`rsa-decrypt`/`eth-root` — the leaks

```python
# factor-from-d: ed-1 → 2^t·r → g^r sequence → a non-trivial x²≡1 → gcd(x-1,n)
# rsa-decrypt: --p --q → phi → d → m
# eth-root: the g roots mod p,q → CRT → pow+format
```

## The verify

`pow(m,e,n)==c` / `p*q==n` — every solve.
