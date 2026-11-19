# Attack shapes — the geometric signatures

## The wrap shape

`c = m^e` with `m^e < n` → `c` is a *perfect power*, not modular. `c` looks
small or an `e`-th power. → `small-e-root`, `nth-root`.

## The broadcast shape

`e` ciphertexts `c_i = m^e mod n_i`, same `m`, coprime `n_i`. The same message
fanned out. → `hastad` (CRT + root).

## The close-prime shape

`n = p·q`, `|p-q|` small → `a=(p+q)/2` just above `√n`, `a²-n` a small square.
→ `fermat`.

## The shared-divisor shape

`n_i`, `n_j` with `gcd>1` — one prime reused across a batch. → `batch-gcd`.

## The smooth-predecessor shape

`p-1` = product of small primes → `a^{B!}≡1 mod p` for `B` ≥ the largest factor.
→ `pollard-pm1`.

## The small-d shape

`d` small → `e·d≡1 mod φ` for `e`≈`n` → a convergent `k/d` of `e/n`. → `wiener`
(`d<n^0.25`), `boneh-durfee` (`d<n^0.292`).

## The shared-modulus shape

`c1=m^e1 mod n`, `c2=m^e2 mod n`, `gcd(e1,e2)=1` → `m=c1^a·c2^b`. → `common-modulus`.

## The partial-knowledge shape

`p` = known-high `a` + unknown-low `x` (`x<n^0.25`) → `f(x)=a+x≡0 mod p` has a
small root. → `coppersmith`.

## The relation shape

`m2=a·m1+b`, both encrypted under `n`,`e` → a shared root of `x^e-c1` and
`(ax+b)^e-c2`. → `franklin-reiter`.

## The leak shape

`d`,`phi`,`dp`,`dq`,`qInv`,`p`,`q` present → arithmetic. → `factor-from-d`,
`crt`, `rsa-decrypt`, `eth-root`.

## The fault shape

`sig` and `sig_faulty` of the same `m` → `gcd(sig_faulty^e - m, n)=q`. → `crt`
Bellcore.
