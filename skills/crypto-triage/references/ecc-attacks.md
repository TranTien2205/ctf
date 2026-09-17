# ECC (Elliptic Curve Cryptography) Attacks

## Common Curve Parameters Reference
```
secp256k1    # Bitcoin curve
secp256r1 (P-256)
secp384r1 (P-384)
secp521r1 (P-521)
```

## Detecting Weak Curve Parameters

### Small Curve Order (Brute-forceable Discrete Log)
```python
# If curve order n is small, use Pohlig-Hellman or brute force
from sage.all import *

E = EllipticCurve(GF(p), [a, b])
P = E(px, py)
Q = E(qx, qy)
n = P.order()

if n < 2**40:  # Small enough to brute force
    for k in range(n):
        if k * P == Q:
            print(f"Private key: {k}")
            break
```

## Invalid Curve Attack
```
# If server doesn't validate that received point lies on the expected curve
# Send points on a different (weaker) curve to leak private key info via
# Chinese Remainder Theorem across multiple invalid curve queries
```

## Nonce Reuse in ECDSA (Critical Vulnerability)

### Same Nonce, Different Messages -> Recover Private Key
```python
# ECDSA signature: (r, s) where s = k^-1 (h + r*d) mod n
# If same k (nonce) used for two signatures with different messages:

# Given (r, s1, h1) and (r, s2, h2) with same r (same k used)
from sympy import mod_inverse

k = ((h1 - h2) * mod_inverse(s1 - s2, n)) % n
d = ((s1 * k - h1) * mod_inverse(r, n)) % n
print(f"Private key: {d}")
```

## Biased/Predictable Nonce (Lattice Attack - HNP)
```
# If nonces have known bias (e.g., leading zero bits, LCG-generated)
# Use Hidden Number Problem (HNP) lattice reduction techniques
# Tools: lattice-based ECDSA nonce recovery scripts (research repos)
```

## Weak Curve / Small Subgroup Attack
```
# If curve has small subgroups, force computation into weak subgroup
# to extract partial private key info via small subgroup confinement
```

## Twist Attacks (Montgomery Curves - e.g. Curve25519 misuse)
```
# If implementation doesn't validate point is on curve (not twist)
# Can leak private key bits by sending points on the twist
```

## Fault Injection (for embedded/hardware targets, theoretical)
```
# Inducing computational faults during scalar multiplication
# to leak key bits via differential fault analysis (mostly hardware-specific)
```

## RSA vs ECC Key Size Equivalence (context for challenge difficulty assessment)
```
RSA 2048-bit  ≈ ECC 224-bit
RSA 3072-bit  ≈ ECC 256-bit
RSA 15360-bit ≈ ECC 521-bit
```

## Common CTF ECC Patterns
```
1. Custom/small curve parameters → brute force discrete log directly
2. Nonce reuse across multiple signatures → linear algebra recovery
3. Missing point validation → invalid curve attack
4. Predictable/weak RNG for nonce → lattice attack (harder, less common in CTF)
```

## Tools
```
SageMath              # Full elliptic curve arithmetic support
ecpy                   # Python ECC library
fastecdsa               # Python ECDSA library
pwnable ECC scripts     # Community CTF-specific ECC attack scripts (GitHub search "ctf ecc attacks")
```
