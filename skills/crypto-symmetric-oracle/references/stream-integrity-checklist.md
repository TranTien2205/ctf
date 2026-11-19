# Stream/CTR integrity — malleability — operational checklist

CTR/stream ciphertext is malleable per-bit: flip a ciphertext bit and the same plaintext bit flips. No integrity means you own the plaintext.

## Checklist

- [ ] Identify the field offset in the plaintext (through the protocol spec or the token structure).
- [ ] delta = known_value XOR wanted_value; xor delta at that offset in the ciphertext.
- [ ] Submit the malleated ciphertext — no garbage block (unlike CBC), so the plaintext parses cleanly.
- [ ] Confirm impact; this is the forge.

## Abort conditions

- Unlike CBC, NO garbage block is produced — the edit is invisible at the crypto layer.
- The plaintext offset you flip must exist — a 10-byte field at offset 200 can't be reached if the message is 100 bytes.
- Ciphertext-only edits don't need a decrypt endpoint — the service's own use of the plaintext is the attack.

## Falsifier

Falsifier — the ciphertext carries a MAC over it: malleation is rejected. Reclassify to mac-forgery or authenticated-boundary.

## Cross-references

`ctr-nonce-reuse.md` · `cbc-bitflip.md` · `token-forgery-workflows.md`
