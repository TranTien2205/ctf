# Theory — the RSA mathematics the attacks exploit

## The construction

```
n = p·q                φ(n) = (p-1)(q-1)
e·d ≡ 1 mod φ(n)
c = m^e mod n          m = c^d mod n
```

Factoring `n` is the trapdoor. RSA is secure iff `p`,`q` can't be recovered —
every attack is a violation of that precondition.

## The six violations

1. **The wrap never happened** — `m^e < n` → `c` is a plain power →
   `integer_nthroot`. Across `e` moduli → CRT → `m^e` → root.
2. **The primes are close** — `|p-q|` small → `n=a²-b²` → `a=(p+q)/2` near `√n`.
3. **A prime divides two moduli** — `gcd(ni,nj)=p` → split both.
4. **p-1 is smooth** — `a^{B!}≡1 mod p` → `gcd(a^{B!}-1,n)=p`.
5. **The exponent leaks the private** — `d<n^0.25` (Wiener CF), `d<n^0.292`
   (Boneh-Durfee lattice), or `gcd(e1,e2)=1` (Bezout).
6. **Bits leak** — `p` partial → Coppersmith small-root; `d`/`phi`/`dp`/`p`,`q`
   → arithmetic; `m2=a·m1+b` → a shared polynomial root; a fault → `gcd` leaks `q`.

## The bounds (the falsifiers)

- **Wiener**: `d < n^0.25` — `k/d` is a CF convergent of `e/n`.
- **Boneh-Durfee**: `d < n^0.292` — bivariate small-root, `f(x,y)=x(A-y)+1 mod e`.
- **Coppersmith-β=½**: unknown `< n^0.25` — `f(x)=a+x≡0 mod p`, `p≥n^0.5`.
- **Coppersmith-message**: `|x| < n^(1/e)` — `f(x)=pad+x≡0 mod n`.
- **small-e**: `m^e < n`.
- **Håstad**: `≥e` coprime `n`, `∏ni > m^e`.
- **common-modulus**: `gcd(e1,e2)=1`.
- **fermat**: `|p-q|` small (the `a` climb is `O(|p-q|)`).
- **pollard-pm1**: `B` ≥ largest `p-1` factor.
- **crt**: `∏pi > m` / a fault / consistent `dp`,`dq`,`qInv`.
- **franklin-reiter**: `m2=a·m1+b` linear, `a`,`b` known.
- **eth-root**: `gcd(e,phi)>1`, `p`,`q` held.

## The verify

`pow(m,e,n)==c` — the definition of decryption. `p*q==n` — the factor. Both are
the *same* trapdoor: they assert the recovered value satisfies the RSA identity.
