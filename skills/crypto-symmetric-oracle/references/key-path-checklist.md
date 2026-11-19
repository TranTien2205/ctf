# Key path — leaked, weak, or derived keys — operational checklist

Sometimes the crypto is honest and the key isn't: hardcoded keys, weak seeds, derived-from-timestamp keys, keys in the handout. Check before building an oracle loop.

## Checklist

- [ ] grep source for 'key', 'secret', 'password', 'seed' — a literal wins immediately.
- [ ] Check for derived keys: sha256(password), time-based seeds, user-input-derived.
- [ ] Check for weak keys in the algorithm's sense (DES weak keys, small RSA keys — different classes).
- [ ] If the key is a PRNG output, that's crypto-prng's class — route there.

## Abort conditions

- A 'key' that's actually a password still needs the right KDF to become a key.
- Keys derived from non-cryptographic PRNG state belong to crypto-prng, not this class.
- Encrypted key files with weak passphrases are a cracking problem (hashcat/john), not an oracle problem.

## Falsifier

Falsifier — no key material leaks and the KDF is honest: the key path is closed. Proceed to oracle attacks.

## Cross-references

`authenticated-boundary.md` · `../crypto-prng/`
