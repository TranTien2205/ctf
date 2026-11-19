# Case studies deep — the full shapes, annotated

## Case A — the `next_prime` keygen

`keygen.py`:
```python
p = getPrime(512); q = next_prime(p)
n = p*q; e = 65537
```
**Sheet**: `n`,`e`,`c`; keygen `next_prime`.
**Discriminator**: `p,q` close → `fermat`.
**Attack**: `crypto_attack.py fermat --n <n>` — converges, `|p-q|` small.
**Verify**: `p*q==n` → `rsa-decrypt` → `pow(m,e,n)==c` → the flag.
**Lesson**: one keygen line names the whole attack.

## Case B — the small-e broadcast

```python
e=3
for n in (n1,n2,n3): send(pow(m,3,n))
```
**Sheet**: `e`=3, three `n`,`c`, same `m`.
**Discriminator**: `c` count ≥ `e` → `hastad`.
**Attack**: CRT `x=m³ mod n1n2n3` → `integer_nthroot(x,3)=m`.
**Verify**: `pow(m,3)==x` → the flag.
**Lesson**: `e` small + same `m` → broadcast, not a single root.

## Case C — the Wiener handout

```python
d = getPrime(64); e = inverse(d, (p-1)*(q-1))
```
**Sheet**: `e` ~ `n` in bits.
**Discriminator**: `e` large → small `d` → `wiener`/`boneh-durfee`.
**Attack**: `wiener` CF → `k/d` convergent → `d`.
**Verify**: `pow(c,d,n)==m`, `pow(m,e,n)==c`.
**Lesson**: a large `e` *is* the small-`d` signature — `e=inverse(d,phi)` ≈ `n`.

## Case D — the `gcd` batch

`keys.json`: 20 moduli, `e`=65537, `c` per `n`.
**Discriminator**: `n` count ≥ 2 → `batch-gcd`.
**Attack**: pairwise `gcd`; `gcd(n3,n7)=p` → `p`,`q`.
**Verify**: `p*q==n3` → `rsa-decrypt` → `pow==c`.
**Lesson**: the *count* is not the bug; the *collision* is — `gcd=1` elsewhere.

## Case E — the partial private key

`priv.pem` with `p`'s high bytes present, low redacted.
**Discriminator**: `p`-bits leak → `coppersmith-high-bits`.
**Attack**: `a`=known-high, `unknown-bits`=256 → `x` → `p=a+x`.
**Verify**: `p|n`, `p*q==n` → `rsa-decrypt`.
**Lesson**: a redacted field is the attack surface.

## Case F — the shared modulus

`n`, `e1`=3, `e2`=17, `c1`, `c2` of the same `m`.
**Discriminator**: 2 `e`, 1 `n`, `gcd=1` → `common-modulus`.
**Attack**: Bezout `m=c1^a·c2^b mod n`.
**Verify**: `pow(m,e1,n)==c1`.
**Lesson**: two exponents on one modulus is the whole bug.

## Case G — `gcd(e,φ)>1`

`e`,`phi` share a factor → `inverse` fails.
**Discriminator**: `gcd(e,phi)>1` → `eth-root`.
**Attack**: `p`,`q` held → the `gcd` candidates → `pow`+format picks.
**Lesson**: `inverse` failing is the *signature* of `eth-root`, not an error.
