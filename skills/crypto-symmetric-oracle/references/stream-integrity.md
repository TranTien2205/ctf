# Stream/CTR integrity — malleability

CTR/stream ciphertext is malleable per-bit: flip a ciphertext bit and the same plaintext bit flips. No integrity means you own the plaintext.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| You know plaintext at some offset | direct edit | xor delta |
| You know structure but not values | guessed-plaintext edit | xor the field delta |
| MAC over the ciphertext | integrity closes | reclassify |

## Steps

1. Identify the field offset in the plaintext (through the protocol spec or the token structure).
2. delta = known_value XOR wanted_value; xor delta at that offset in the ciphertext.
3. Submit the malleated ciphertext — no garbage block (unlike CBC), so the plaintext parses cleanly.
4. Confirm impact; this is the forge.

## Falsifier

Falsifier — the ciphertext carries a MAC over it: malleation is rejected. Reclassify to mac-forgery or authenticated-boundary.

## Traps

- Unlike CBC, NO garbage block is produced — the edit is invisible at the crypto layer.
- The plaintext offset you flip must exist — a 10-byte field at offset 200 can't be reached if the message is 100 bytes.
- Ciphertext-only edits don't need a decrypt endpoint — the service's own use of the plaintext is the attack.

## Commands

```bash
python3 tools/crypto_attack.py crib-drag --ct1 <h> --ct2 <h> --crib '<known>'
```

## Cross-references

`ctr-nonce-reuse.md` · `cbc-bitflip.md` · `token-forgery-workflows.md`
