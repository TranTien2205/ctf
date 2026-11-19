# Theory catalogue — the identity → the family → the attack

## The identity

`n=p·q`, `φ=(p-1)(q-1)`, `ed≡1 mod φ`, `c=m^e mod n`, `m=c^d mod n`.
`pow(m,e,n)==c` is the verify.

## Wrap — `m^e<n` → `c` a plain power

- `m=c^{1/e}` → `small-e-root`/`nth-root`.
- `m^e<∏ni` → CRT → `c^{1/e}` → `hastad`.
- The bound: `m^e<n` — the wrap never engaged.

## Gap — `|p-q|` small → `n=a²-b²`

- `a=(p+q)/2` near `√n`; `a²-n=((p-q)/2)²` square → `fermat`.
- The bound: the `a` walk is `O(|p-q|)`.

## Divisor — a shared/smooth factor

- `gcd(ni,nj)=p` → `batch-gcd` — a shared `p`.
- `gcd(a^{B!}-1,n)=p` (`p-1` `B`-smooth) → `pollard-pm1`.

## Exponent — `ed≡1 mod φ` leaks `d`

- `d<n^0.25` → CF `k/d` → `wiener`.
- `d<n^0.292` → LLL `f(x,y)=x(A-y)+1` → `boneh-durfee`.
- `gcd(e1,e2)=1` → Bezout `m=c1^a·c2^b` → `common-modulus`.
- `d`/`phi`/`dp`/`qInv`/`p`,`q` held → `factor-from-d`/`crt`/`rsa-decrypt`.

## Partial — bits → Coppersmith

- `p=a+x`, `|x|<n^0.25` → `coppersmith-high-bits`/`-core`.
- `m` pad, `|x|<n^(1/e)` → partial-message.

## Relation/leak — the structure

- `m2=a·m1+b` → poly `gcd` → `franklin-reiter`.
- `sig`+`sig_faulty` → `gcd(s'^e-m,n)` → `crt` Bellcore.
- `gcd(e,phi)>1` → `g` roots → `eth-root`.

## The bounds, ordered

```
d<n^0.25 wiener · d<n^0.292 boneh-durfee · window n^0.25/n^(1/e) coppersmith
m^e<n small-e · ≥e n's hastad · gcd=1 common-modulus · |p-q| fermat
B≥factor pollard-pm1 · ∏pi>m crt · linear franklin-reiter · gcd(e,phi)>1 eth-root
```
