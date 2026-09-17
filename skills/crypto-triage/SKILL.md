---
name: crypto-triage
description: >
  Cryptography challenge triage and solving. Use when CTF challenge involves
  encrypted data, weak algorithms, known attacks, or custom crypto. Supports
  classical ciphers, RSA, AES, ECC, hash attacks, and common CTF crypto.
tags: [crypto, rsa, aes, classical, hash, cipher]
environment: [ctf, lab]
---

# Cryptography CTF Triage

## Quick Identification

### Algorithm Detection
```
Single character shift → Caesar/ROT-n
Substitution table → Substitution cipher
Key + XOR → XOR cipher
Repeated blocks → ECB mode
IV + ciphertext → CBC/CTR/GCM
Public key → RSA/ECC
Short key + large data → AES/DES
Hash value → MD5/SHA1/SHA256
```

## Tools Reference
| Tool | Use Case |
|------|----------|
| RsaCtfTool | RSA attacks |
| CyberChef | Multi-format crypto |
| hashcat/john | Password cracking |
| factordb.com | Factor large numbers |
| yafu | Integer factorization |
| SageMath | Complex crypto math |
| zlib deflate | Decompression |
| quipqiup.com | Substitution ciphers |

## Decision Tree
- RSA challenge → `references/rsa-attacks.md`
- AES/DES → `references/block-cipher.md`
- Classical cipher → `references/classical.md`
- Hash challenge → `references/hash-attacks.md`
- XOR challenge → `references/xor-analysis.md`
- ECC challenge → `references/ecc-attacks.md`

## References
- `references/rsa-attacks.md` - RSA attack techniques
- `references/block-cipher.md` - Block cipher modes and attacks
- `references/classical.md` - Classical cipher solving
- `references/hash-attacks.md` - Hash collision and extension
- `references/xor-analysis.md` - XOR cipher analysis
- `references/ecc-attacks.md` - Elliptic curve attacks

## Discipline

- Collect every parameter and size before choosing an attack; a named attack on
  guessed parameters wastes the budget.
- One technique class at a time. Budget and escalation as in
  `../LOOP_DISCIPLINE.md`.
- A recovered value is a hypothesis until it decrypts or validates against the
  supplied artifact.
