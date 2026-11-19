# Stream/CTR integrity — malleability — case catalogue

CTR/stream ciphertext is malleable per-bit: flip a ciphertext bit and the same plaintext bit flips. No integrity means you own the plaintext.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | You know plaintext at some offset | direct edit | xor delta |
| 2 | You know structure but not values | guessed-plaintext edit | xor the field delta |
| 3 | MAC over the ciphertext | integrity closes | reclassify |

## Falsifier

Falsifier — the ciphertext carries a MAC over it: malleation is rejected. Reclassify to mac-forgery or authenticated-boundary.

## Coverage notes

- Unlike CBC, NO garbage block is produced — the edit is invisible at the crypto layer.
- The plaintext offset you flip must exist — a 10-byte field at offset 200 can't be reached if the message is 100 bytes.
- Ciphertext-only edits don't need a decrypt endpoint — the service's own use of the plaintext is the attack.

## Cross-references

`ctr-nonce-reuse.md` · `cbc-bitflip.md` · `token-forgery-workflows.md`
