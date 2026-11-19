# CBC IV prediction — the BEAST-shaped case — index

When the IV for the NEXT message is predictable (chained from the previous
ciphertext block — the old TLS1.0 bug), chosen plaintext verifies guesses.

## Companions

- `cbc-iv-prediction-deep.md` — boundary conditions and the failure shape
- `cbc-iv-prediction-checklist.md` — the same content as an ordered checklist
- `cbc-iv-prediction-map.md` — the lookup table alone
- `../field-notes.md` — where outcomes land
