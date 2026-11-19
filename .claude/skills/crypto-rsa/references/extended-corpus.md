# Extended corpus — every attack, one paragraph

## batch-gcd
Compute `gcd(n_i, n_j)` pairwise. A `gcd>1` is a shared prime — `p=gcd`, `q=n/p`.
**Needs** ≥2 moduli from the same RNG. **Bound**: a collision must exist.
**Verify**: `p*q==n`. **Negative**: all `gcd=1` — no reuse.

## common-modulus
`c1=m^e1 mod n`, `c2=m^e2 mod n`, `gcd(e1,e2)=1` → Bezout `a·e1+b·e2=1` →
`m=c1^a·c2^b mod n`. **Bound**: `gcd=1`. **Verify**: `pow(m,e1,n)==c1`.
**Negative**: `gcd>1` → `m^gcd`, not `m` (then `nth-root` if `m^gcd<n`).

## fermat
`a=isqrt(n)+1`; while `a²-n` not a square, `a+=1`; then `n=(a-b)(a+b)`. Converges
when `|p-q|` small. **Bound**: `|p-q|` small. **Verify**: `p*q==n`.
**Negative**: `a` past budget — primes balanced.

## wiener
`d<n^0.25` → a convergent `k/d` of `e/n` gives `d`. **Bound**: `d<n^0.25` —
`e≈n` is the tell. **Verify**: `pow(c,d,n)==m`. **Negative**: `d≥n^0.25` →
`boneh-durfee`.

## boneh-durfee
`f(x,y)=x(A-y)+1 mod e`, `A=n+1`; LLL for `(k, p+q)` → `d`. **Bound**:
`d<n^0.292`. `boneh-durfee-escalate` raises `m`,`t`. **Verify**:
`pow(c,d,n)==m`. **Negative**: `d≥n^0.292` — small-d closed.

## coppersmith-high-bits / -core
`f(x)=a+x≡0 mod p`, `p≥n^0.5`, `|x|<n^0.25` → LLL → `x` → `p=a+x`. **Bound**:
the unknown `<n^0.25`. **Verify**: `p|n`. **Negative**: window `<n^0.25` — need
a bigger leak.

## small-e-root / nth-root
`m^e<n` → `m = c^(1/e)` exactly. **Bound**: `m^e<n`. **Verify**: `pow(m,e)==c`.
**Negative**: `m^e≥n` — wrapped → `hastad`/`coppersmith`.

## hastad
same `m` to `e` coprime `n` → CRT → `m^e mod ∏ni` → `e`th root. **Bound**: `≥e`
ciphertexts, `∏ni>m^e`, no pad. **Verify**: `pow(m,e)==x`. **Negative**: `<e`
n's or a pad.

## pollard-pm1
`a^{B!}≡1 mod p` for `B`≥largest `p-1` factor → `gcd(a^{B!}-1,n)=p`. **Bound**:
`p-1` `B`-smooth. **Verify**: `gcd=p`. **Negative**: `gcd=1` for `B` — `p-1`
not smooth enough.

## franklin-reiter
`m2=a·m1+b`, same `n`,`e` → `gcd(x^e-c1, (ax+b)^e-c2)=x-m`. **Bound**: linear
relation, `a`,`b` known. **Verify**: `pow(m,e,n)==c`. **Negative**: relation
not linear.

## crt
Three forms: residues (`∏pi>m` → `m`), a faulty sig (`gcd(s'^e-m,n)=q`), or
`dp`,`dq`,`qInv` (`p`/`q`/`d` recovery). **Verify**: `pow(m,e,n)==c` or
`p*q==n`. **Negative**: `∏pi≤m` or no fault.

## factor-from-d
`k=ed-1` is a multiple of `φ` → split `k=2^t·r` → random `g`, `g^r` chain → a
non-trivial `x` with `x²≡1 mod n` → `gcd(x-1,n)=p`. **Bound**: `d`/`phi` held.
**Verify**: `p*q==n`.

## rsa-decrypt / eth-root
`m=c^d mod n` (or the `gcd(e,phi)` candidates for `eth-root`). **Verify**:
`pow(m,e,n)==c`. `eth-root` → try each `gcd` candidate, `pow`+format picks.
