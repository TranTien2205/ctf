# Worked examples deep — annotated solves with the verify inline

## fermat, fully annotated

`q = next_prime(p)` → `p,q` within ~a few thousand. `a=(p+q)/2` sits just above
`sqrt(n)`; `a²-n = b² = ((p-q)/2)²`, a small square.
```python
a = isqrt(n) + 1
# a²-n is ((p+q)/2)² - pq = ((p-q)/2)² — a perfect square when it lands
b, ok = integer_nthroot(a*a - n, 2)
```
The `a` climb is `O(|p-q|/2)` — for `next_prime` that's tens of iterations.
`p=a-b`, `q=a+b`. Then `phi`, `d`, `m`. **`p*q==n` proves the split**.

## wiener, fully annotated

`ed ≡ 1 mod phi` → `ed - k·phi = 1` for some `k` → `|e/n - k/d| < 1/(3d²)` —
`k/d` is a convergent of `e/n` when `d < n^0.25`. The CF expansion of `e/n`
enumerates the convergents; for each `k_i/d_i` candidate, `phi'=(e·d_i-1)/k_i`
→ check the quadratic `x²-(n-phi'+1)x+n=0` for integer roots. **`pow(c,d,n)==m`
proves the `d`**.

## boneh-durfee, fully annotated

`ed ≡ 1 mod phi` → `ed - k(n+1-p-q) = 1` → `e·d + k·(p+q) ≡ 1+k(n+1) mod e` →
`f(x,y)=x(A-y)+1 ≡ 0 mod e` has root `(k, p+q)`, `A=n+1`. Coppersmith's
bivariate LLL recovers `(k, s)` for `d<n^0.292`; `d=(e·d mod e)`... the lattice
returns `d`/`(k,s)` → `p`,`q` from `s=p+q`. **`pow(c,d,n)==m` proves it**.

## hastad, fully annotated

`c_i = m³ mod n_i` for `i=1,2,3`. CRT: `x ≡ c_i mod n_i` → `x = m³ mod n1n2n3`.
Since `m³ < n1n2n3`, `x = m³` exactly → `m = x^{1/3}`. **`pow(m,3)==x` proves
it** — the CRT product *must* exceed `m^e` for the root to be `m`.

## common-modulus, fully annotated

`c1=m^3`, `c2=m^17` mod `n`. `gcd(3,17)=1`, `a·3+b·17=1` → `a=-5,b=1`? `-15+16=1` no; `5·3 -1·17 = -2`... solve `a·e1+b·e2=1` → `m = c1^a · c2^b mod n`
(a negative `a` means `pow(c1,a,n)` — Python handles modular inverse).
**`pow(m,e1,n)==c1` proves it**.

## pollard-pm1, fully annotated

If `p-1 | B!` → `a^{B!} ≡ 1 mod p` → `p | a^{B!}-1` and `p | n` →
`gcd(a^{B!}-1, n) = p`. The loop `a=pow(a,j,n)` for `j=2..B` computes
`a^{B!}`. **`gcd>1` proves the factor** — `1<gcd<n` is a non-trivial factor.

## coppersmith, fully annotated

`p = a + x`, `a` the known high bits, `|x|<n^0.25`. `f(x)=a+x ≡ 0 mod p`. LLL on
the `f` lattice finds a polynomial with a small integer root `x0` → `p=a+x0`.
**`p|n` proves it**.

## eth-root, fully annotated

`gcd(e,phi)=g>1` → `e` not invertible mod `phi`. `p`,`q` held → compute the `g`
`e`th-root candidates mod `p` and mod `q` → CRT → `g` candidates mod `n` →
`pow(m_i,e,n)==c` + flag format picks the true one.
