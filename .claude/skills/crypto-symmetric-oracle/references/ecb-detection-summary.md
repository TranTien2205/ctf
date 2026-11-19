# ECB detection — one request, deterministic — summary

ECB leaks structure: identical plaintext blocks produce identical ciphertext blocks. Detection needs one request holding enough repeated material to fill two blocks — no statistical test, no second round-trip.

## Signal → route

- Identical plaintext block appears twice → identical ciphertext block pair → byte-at-a-time or cut-and-paste
- Repeated input never repeats in output → alignment probe
- Ciphertext length jumps in block-size steps → block-size measurement
- Ciphertext length tracks input 1:1 → keystream-reuse test

## Falsifier

Falsifier — no duplicated 16-byte window appears anywhere in a 48-byte repeated input after ruling out misalignment, and the length grows continuously rather than in block steps: the mode is not ECB.
