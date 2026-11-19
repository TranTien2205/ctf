# Theory deep — the proofs behind the attacks

## Why Wiener works

`ed ≡ 1 mod φ` → `ed - kφ = 1` for some `k<d` → `|e/n - k/d| = |edk - knφ - kd|`
… with `φ ≈ n` and `d < n^0.25` → `|e/n - k/d| < 1/(3d²)` → `k/d` is a convergent
of `e/n` by Legendre's theorem. Enumerate CF convergents of `e/n`; each `k_i/d_i`
gives a candidate `d_i`; `pow(c,d_i,n)` verifies.

## Why Boneh-Durfee works

`ed ≡ 1 mod φ` → `ed + k(n+1-p-q) = 1 + kn` → `e·d + k·s ≡ 1 + k(n+1) mod e`
with `s=p+q`. Set `f(x,y) = x(A-y) + 1 ≡ 0 mod e`, `A=n+1`; `f(k,s)=0`.
`k ≈ d < n^0.292`, `s < n^0.5` → a bivariate Coppersmith small-root → LLL
recovers `(k,s)` → `d` and `p`,`q`. The `0.292` bound is the LLL approximation
ceiling.

## Why Coppersmith works

`f(x) = a + x ≡ 0 mod p`, `p ≥ n^β`. For `β=½`, a root `|x0| < n^(β²/d) = n^0.25`
(for `f` linear, `d=1`). LLL on the `f`-lattice finds a polynomial `g` with
`g(x0)=0` over the integers → `x0` → `p = a+x0`. The `n^0.25` bound is `β²`.

## Why Fermat works

`n=pq`, `|p-q|` small → `a=(p+q)/2` near `√n`, `a²-n = ((p-q)/2)²`. Walk `a`
from `⌈√n⌉`; `a²-n` is a square `b²` → `n=(a-b)(a+b)`. `O(|p-q|)` iterations.

## Why batch-gcd works

`n_i = p·q_i`, `n_j = p·q_j` → `gcd(n_i,n_j)=p`. A reused prime is a shared
factor — the RNG reused `p` across two keys.

## Why pollard-pm1 works

`p-1 | B!` → `a^{B!} ≡ 1 mod p` (Fermat) → `p | a^{B!}-1` and `p | n` →
`gcd(a^{B!}-1, n) = p`. The `B`-smoothness of `p-1` is the condition.

## Why common-modulus works

`gcd(e1,e2)=1` → `a·e1+b·e2=1` (Bezout) → `m^{a·e1+b·e2}=m` →
`m = c1^a · c2^b mod n`. The two exponents factor `m` back out.

## Why Håstad works

`c_i = m^e mod n_i`, `n_i` coprime → CRT: `x ≡ c_i mod n_i` → `x = m^e mod ∏ni`.
`m^e < ∏ni` → `x = m^e` → `m = x^{1/e}`.

## Why Franklin-Reiter works

`c1=x^e`, `c2=(ax+b)^e` mod `n` — the polynomials `x^e-c1` and `(ax+b)^e-c2`
share the root `x=m` → `gcd` of them (in `Z_n[x]`) = `x-m`.

## Why Bellcore works

`s' = m^{dp} mod p` correct, `s'` wrong mod `q` → `s'^e - m ≡ 0 mod p`,
`≢0 mod q` → `gcd(s'^e - m, n) = p` (or `q`).

## Why eth-root works

`gcd(e,phi)=g` → `m^e` has `g` roots mod `n` (via CRT of the `g_p` roots mod `p`
and `g_q` roots mod `q`) → enumerate them; `pow`+format picks.
