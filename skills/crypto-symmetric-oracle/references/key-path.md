# Key path — leaked, weak, or derived keys

Sometimes the crypto is honest and the key isn't: hardcoded keys, weak seeds, derived-from-timestamp keys, keys in the handout. Check before building an oracle loop.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Key in source or handout | use it directly | decrypt |
| Seed from time() or pid | searchable seed space | brute-force seed |
| Key derived from password | KDF weakness | check the KDF |

## Steps

1. grep source for 'key', 'secret', 'password', 'seed' — a literal wins immediately.
2. Check for derived keys: sha256(password), time-based seeds, user-input-derived.
3. Check for weak keys in the algorithm's sense (DES weak keys, small RSA keys — different classes).
4. If the key is a PRNG output, that's crypto-prng's class — route there.

## Falsifier

Falsifier — no key material leaks and the KDF is honest: the key path is closed. Proceed to oracle attacks.

## Traps

- A 'key' that's actually a password still needs the right KDF to become a key.
- Keys derived from non-cryptographic PRNG state belong to crypto-prng, not this class.
- Encrypted key files with weak passphrases are a cracking problem (hashcat/john), not an oracle problem.

## Commands

```bash
python3 tools/crypto_attack.py list
```

## Cross-references

`authenticated-boundary.md` · `../crypto-prng/`
