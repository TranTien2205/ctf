# Quick reference deep — the one-page RSA card

## The commands

```bash
python3 tools/crypto_attack.py list                  # the inventory + bounds
python3 tools/crypto_attack.py <id> --help           # the flags for <id>
python3 tools/crypto_attack.py <id> <flags>          # run the attack
```

## The discriminators (first yes wins)

```
d/phi/dp/p,q  → factor-from-d/rsa-decrypt/eth-root
≥2 moduli      → batch-gcd
same m, e n's  → hastad
2 e on 1 n     → common-modulus
p,q close      → fermat
e~n            → wiener → boneh-durfee
p-bits         → coppersmith-high-bits/-core
e=3,m short    → small-e-root/nth-root
p-1 smooth     → pollard-pm1
m2=a·m1+b      → franklin-reiter
residues/fault → crt
gcd(e,phi)>1   → eth-root
```

## The bounds

```
d<n^0.25    wiener
d<n^0.292   boneh-durfee
window<n^0.25  coppersmith
m^e<n       small-e/nth-root
≥e n's      hastad
gcd=1       common-modulus
|p-q| small fermat
B≥factor    pollard
∏pi>m       crt
linear      franklin-reiter
gcd(e,phi)>1 eth-root
```

## The verify

```
pow(m,e,n)==c     plaintext
p*q==n            factor
pow(c,d,n)==m     d
```

## The toolchain

`tools/crypto/` stdlib-only · `fpylll` absent → pure-python LLL · `lll_backend`
reports · `sympy`/`Crypto` present.

## The honest status

Catalogue — no local solve. `../field-notes.md` grows with real solves.
