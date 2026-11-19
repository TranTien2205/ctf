# Real-world cases deep — the challenge shapes, annotated

## The `p`,`q` weakness shapes

### `q=next_prime(p)` → `fermat`
```python
p = getPrime(512); q = next_prime(p); n = p*q
```
`n=a²-b²`, `a` near `√n` → `fermat --n` walks a few steps → `p`,`q`. The gap is
`O(1)` — a close-prime.

### A seeded RNG → `batch-gcd`
```python
random.seed(0xDEAD); p=getPrime(512); q=getPrime(512)   # a small/known seed
# or a key-server reusing p across keys
```
A small/known seed regenerates `p`,`q`; a reused `p` collides → `gcd`.

### `p-1` smooth → `pollard-pm1`
```python
p = product of small primes + 1   # 'a fast prime'
```
`p-1` `B`-smooth → `gcd(a^{B!}-1,n)=p`.

## The `e`/`d` weakness shapes

### `e`=3, `m` short → `small-e-root`
```python
e=3; c=pow(m,3,n)   # m³<n → c = m³
```
`m=c^{1/3}` — `pow` verify.

### `d` small → `wiener`/`boneh-durfee`
```python
d = getPrime(64)   # or getPrime(300)
e = inverse(d, phi)   # e ≈ n in size — the tell
```
`d<n^0.25` → `wiener`; `n^0.25..n^0.292` → `boneh-durfee`.

## The partial-info shapes

### `p` partial → `coppersmith`
```python
print(hex(p)[:300] + 'XXXX...')   # high half of p
```
`p=a+x`, `|x|<n^0.25` → `coppersmith-high-bits`.

### `d`/`phi`/`dp` leak → `factor-from-d`/`crt`
```python
print(d)   # or dp= d%(p-1), dq=d%(q-1), qInv in a partial private key
```
`d`/`phi` held → `factor-from-d`; `dp` → `crt` manual.

## The multi-modulus shapes

### A `.json` of `n` → `batch-gcd`
```json
[{"n": ..., "e": 65537}, ...]   # 100 moduli
```
`gcd` pairwise → a shared prime.

### A broadcast → `hastad`
```python
for n in ns: send(pow(m,3,n))   # e=3, same m, 3 coprime n
```
CRT + root → `m`.

### A shared modulus → `common-modulus`
```python
encrypt(m, e1, n); encrypt(m, e2, n)   # same n
```
Bezout → `m`.

## The relation shapes

### `m2=a·m1+b` → `franklin-reiter`
```python
m2 = 2*m1 + 7; c1=pow(m1,e,n); c2=pow(m2,e,n)
```
Poly `gcd` → `m`.

### A `sig` fault → `crt` Bellcore
```python
sig_correct; sig_faulty   # a glitch in the CRT half
```
`gcd(s'^e-m,n)` → `q` (manual).

## The honest status

All catalogue shapes — no local solve.
