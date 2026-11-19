# Verify — the cryptographic gate

## The two gates

```python
pow(m, e, n) == c    # a plaintext m
p * q == n           # a factor pair p, q
```

Every recovery must pass one. A value that fails is a candidate; an attack that
ran is not proof.

## The extended gate (d recovery)

```python
m = pow(c, d, n)
assert pow(m, e, n) == c    # d decrypts and re-encrypts
```

## The phi consistency

```python
# n - phi + 1 = p + q   for n = p*q
assert n - phi + 1 == p + q
```

## The padded-plaintext rule

`m` is a padded block → `pow(m,e,n)==c` held on the *padded* block; the flag is
inside it:
```python
b = long_to_bytes(m)
# PKCS#1 v1.5: \x00\x02<padding>\x00<message> — or OAEP-unpad
```

## The eth-root rule

`gcd(e,phi)=g` → `g` candidate `m`'s → `pow(m_i,e,n)==c` holds for all; the flag
*format* (`flag{`, `CTF{`, printable) picks the true root.

## The Bellcore rule

```python
q = gcd(pow(s_faulty, e, n) - m, n)
assert 1 < q < n and n % q == 0
```

## The falsifier

An attack's *bound* is its falsifier — `d<n^0.292`, window `≥n^0.25`, `m^e<n`,
`≥e` n's, `gcd=1`, `|p-q|` small, `B`≥factor. A bound exceeded is a negative
result, not a retry.

## The rule

`pow(m,e,n)==c` or `p*q==n` — deterministic, run them. Never claim a recovery
without one.
