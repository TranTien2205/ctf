# Decision catalogue — every branch, its command

## The leak branches

```
d held          → crypto_attack.py factor-from-d --n --e --d
phi held        → crypto_attack.py factor-from-d --n --phi
dp,dq,qInv held → crypto_attack.py crt --residues --moduli
p,q held        → crypto_attack.py rsa-decrypt --c --e --factors --c
gcd(e,phi)>1    → crypto_attack.py eth-root --c --e --factors
```

## The batch branches

```
≥2 n, same gen  → crypto_attack.py batch-gcd --moduli n1 n2 ...
same m, e n's   → crypto_attack.py hastad --pairs c1..ce --moduli n1..ne --e e
```

## The single-modulus branches

```
p,q close       → crypto_attack.py fermat --n
e~n             → crypto_attack.py wiener --n --e
                  then boneh-durfee / boneh-durfee-escalate
e=3,m short     → crypto_attack.py small-e-root --c --e --n
p-1 smooth      → crypto_attack.py pollard-pm1 --n --b
2 e on 1 n      → crypto_attack.py common-modulus --n --e1 --c1 --e2 --c2
p-bits          → crypto_attack.py coppersmith-high-bits --n --known --bits
m2=a·m1+b       → franklin-reiter --n --e --a --b --c1 --c2
residues/fault  → # crt --residues/--moduli only; the Bellcore fault is a manual gcd
```

## The arg help

`crypto_attack.py <id> --help` — the exact flag names per id; they differ.

## The verify (the last step)

```python
assert pow(m, e, n) == c   # plaintext
assert p * q == n          # factor
```
