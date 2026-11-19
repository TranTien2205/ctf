# CBC bit-flipping — targeted plaintext edits — surface variants

CBC decrypts block i as Dec(C_i) XOR C_{i-1}: flip a bit in C_{i-1} and the same bit flips in P_i while C_{i-1}'s own plaintext is scrambled. Controlled edits cost one block of garbage.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| You need 'user' → 'admin' or a number changed in a CBC token | bit-flip applies | locate offset, flip bytes |
| The token's IV is prepended and attacker-controlled | first block is fully controllable | edit P_1 via IV |
| Scrambled block must stay parseable | needs structure tolerant to garbage | use IV or a don't-care block |

## Variant-specific traps

- Editing the IV changes ONLY block 1 — a common mistake is to edit the IV expecting a mid-message change.
- The scrambled-block garbage must not contain a quote/brace that breaks the surrounding parser.
- PKCS#7 on the last block: edits near the end can corrupt padding and cause a reject unrelated to your target field.
- Some tokens prefix a length or CRC; the CRC block scrambles too and must be recomputed or bypassed.

## Falsifier

Falsifier — the token is authenticated and any modification is rejected, or the parser rejects the inevitable garbage block: bit-flip survives neither.

## Cross-references

`cbc-padding-oracle.md` · `cbc-iv-equals-key.md` · `token-forgery-workflows.md`
