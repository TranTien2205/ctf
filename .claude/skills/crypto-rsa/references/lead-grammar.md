# Lead grammar — the signal phrases → the class

## The phrases

- "n = ...", "e = 65537", "c = ..." → `crypto-rsa`.
- "same message to N recipients" → `hastad`.
- "next_prime" / "close primes" / "q = p + ..." → `fermat`.
- "small private exponent" / "d is small" → `wiener`/`boneh-durfee`.
- "leaked", "partial key", "redacted" → `coppersmith`/`crt`/`factor-from-d`.
- "shared prime" / "reused" / "a batch of keys" → `batch-gcd`.
- "p-1" / "smooth" → `pollard-pm1`.
- "m2 = a*m1 + b" / "related" → `franklin-reiter`.
- "residue" / "CRT" / "faulty signature" / "dp","dq","qInv" → `crt`.
- "g, h = g^x", "curve", "order", "dlog" → `crypto-ecc-dlog`.
- "keystream", "seed", "predict" → `crypto-prng`.
- "encrypt/decrypt/sign query", "oracle", a menu → `crypto-symmetric-oracle`.
- "xor", "vigenere", "substitution" → `crypto-classical`.
- a URL, an endpoint → a `web-*` class.
