# Evasion — how the class hides

- `e`=65537 deflects — read the keygen, not `e`.
- a huge `n` misdirects — the bug is a precondition, not the size.
- a clean `n`,`e`,`c` — the bug is the *generator*: `next_prime`,`seed`,`p-1`.
- a `.pem` with a field redacted — that field is the attack surface.
- `e` huge → the small-`d` tell, not "strong".
- a `.json` of moduli → a `batch-gcd`/`hastad` target.
- a bound *just* exceeded → a negative, not "hard".
- a pad on `m` → `pow` held on the padded block; strip for the flag.
- a socket that *re-encrypts* → `crypto-symmetric-oracle`.
- proper RSA → the class falsifier → the protocol bug.
See `evasion-deep.md`.
