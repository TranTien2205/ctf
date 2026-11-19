# Key path — leaked, weak, or derived keys — case catalogue

Sometimes the crypto is honest and the key isn't: hardcoded keys, weak seeds, derived-from-timestamp keys, keys in the handout. Check before building an oracle loop.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Key in source or handout | use it directly | decrypt |
| 2 | Seed from time() or pid | searchable seed space | brute-force seed |
| 3 | Key derived from password | KDF weakness | check the KDF |

## Falsifier

Falsifier — no key material leaks and the KDF is honest: the key path is closed. Proceed to oracle attacks.

## Coverage notes

- A 'key' that's actually a password still needs the right KDF to become a key.
- Keys derived from non-cryptographic PRNG state belong to crypto-prng, not this class.
- Encrypted key files with weak passphrases are a cracking problem (hashcat/john), not an oracle problem.

## Cross-references

`authenticated-boundary.md` · `../crypto-prng/`
