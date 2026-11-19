# Detection variants — the fingerprint in every presentation

## Variant: a `.txt` of numbers
```
n = 0x9f3a...
e = 65537
c = 0x4b2e...
```
→ the sheet; the comment (or the file name) hints the attack. `e`=65537 → the
bug is in `p`,`q` or a leak, not `e`.

## Variant: a `keygen.py`
```python
p = getPrime(512); q = next_prime(p)
n = p*q; e = 65537; d = inverse(e,(p-1)*(q-1))
```
→ `next_prime` → `fermat`. One line names the whole attack.

## Variant: a batch
```json
[{"n":...,"e":65537,"c":...},{"n":...,"e":65537,"c":...},...]
```
→ `batch-gcd` for a shared prime; `hastad` if the same `m` under `e` coprime
`n`'s.

## Variant: a small-e broadcast
```python
e=3
for n in (n1,n2,n3): c_i = pow(m,e,n_i)
```
→ `hastad` — `m` identical across `e` coprime `n`'s.

## Variant: a private-key leak
```
-----BEGIN RSA PRIVATE KEY-----  (with fields: n, e, dp, dq, qInv — d redacted)
```
→ `crt` if `dp`,`dq`,`qInv` consistent; `coppersmith` if `p` partial; `factor-from-d` if `d`/`phi`.

## Variant: a signature pair
```
sig_correct = pow(m, d, n); sig_faulty = <fault>
```
→ `crt` Bellcore — `gcd(sig_faulty^e - m, n)`.

## Variant: a public PEM
```
-----BEGIN PUBLIC KEY-----
```
→ `n`,`e` only. The bug is in the number relation, not the file.

## Variant: a socket
```
nc host port → n=... e=... c=...
```
→ transport; the numbers. If it re-encrypts → `crypto-symmetric-oracle`.

## Variant: two ciphertexts, two exponents, one n
```
n, e1, e2, c1, c2   (same m)
```
→ `common-modulus` — Bezout.

## Variant: a relation
```
m2 = a*m1 + b;  c1, c2 under same n,e
```
→ `franklin-reiter`.

## The rule

The presentation changes; the discriminator doesn't. The sheet is the same —
`n`,`e`,`c`,leaks,keygen.
