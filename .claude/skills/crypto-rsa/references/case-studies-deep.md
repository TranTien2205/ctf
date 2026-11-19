# Case studies deep — the annotated challenge shapes

## `fermat` — `q=next_prime(p)`

```python
p = getPrime(512); q = next_prime(p); n = p*q
```
`|p-q|` ~ hundreds → `fermat` climbs `a` in `O(|p-q|)` → `p`,`q`.

## `wiener` — `d` small

```python
d = getPrime(64); e = inverse(d, phi)   # e ≈ n
```
`d=64-bit<n^0.25` → `wiener` CF → `d`.

## `batch-gcd` — a seeded RNG / shared `p`

```python
random.seed(0); n1 = p*q1; n2 = p*q2   # p reused
```
`gcd(n1,n2)=p` → both split.

## `small-e-root` — `e=3`, `m` short

```python
e=3; c=pow(m,3,n)   # m³<n
```
`m=c^{1/3}` — the wrap never engaged.

## `hastad` — broadcast

```python
for n in [n1,n2,n3]: send(pow(m,3,n))   # same m, e=3
```
CRT + root → `m`.

## `common-modulus` — shared `n`

```python
encrypt(m,e1,n); encrypt(m,e2,n)   # gcd(e1,e2)=1
```
Bezout → `m`.

## `pollard-pm1` — `p-1` smooth

```python
p = smooth_prime(512)   # p-1 a product of small primes
```
`gcd(a^{B!}-1,n)=p`.

## `coppersmith` — `p` bits

```python
print(hex(p)[:200] + 'XXXX...')   # high half of p
```
`p=a+x`, `|x|<n^0.25` → `coppersmith-high-bits`.

## `franklin-reiter` — `m2=a·m1+b`

```python
m2 = 2*m1 + 7; c1 = pow(m1,e,n); c2 = pow(m2,e,n)
```
Poly `gcd` → `m`.

## `crt` — Bellcore / dp / residues

`sig`+`sig_faulty` → `gcd` → `q` · `dp`/`qInv` → `p` · `m mod pi` → `m`.

## `factor-from-d`/`rsa-decrypt`/`eth-root` — leaks

`d`/`phi`/`p`,`q`/`gcd(e,phi)>1` — arithmetic, not a search.
