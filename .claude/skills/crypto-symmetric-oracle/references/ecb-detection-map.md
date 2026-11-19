# ECB detection — one request, deterministic — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| Identical plaintext block appears twice → identical ciphertext block pair | ECB confirmed | byte-at-a-time or cut-and-paste |
| Repeated input never repeats in output | CBC/CTR/stream or ECB+prefix desync | alignment probe |
| Ciphertext length jumps in block-size steps | block cipher (ECB or CBC) | block-size measurement |
| Ciphertext length tracks input 1:1 | stream cipher or CTR | keystream-reuse test |

## Falsifier

Falsifier — no duplicated 16-byte window appears anywhere in a 48-byte repeated input after ruling out misalignment, and the length grows continuously rather than in block steps: the mode is not ECB.
