# CBC bit-flipping — targeted plaintext edits — operational checklist

CBC decrypts block i as Dec(C_i) XOR C_{i-1}: flip a bit in C_{i-1} and the same bit flips in P_i while C_{i-1}'s own plaintext is scrambled. Controlled edits cost one block of garbage.

## Checklist

- [ ] Find which ciphertext block covers the target plaintext bytes (vary input, watch which block changes).
- [ ] delta = P_want XOR P_have; xor delta into the PREVIOUS ciphertext block (or the IV for block 1).
- [ ] The previous block decrypts to garbage — ensure it falls in a field the parser ignores.
- [ ] If only the IV is malleable and you need a deeper block, chain: corrupt C_{i-1} to fix P_i while accepting garbage in P_{i-1}.

## Abort conditions

- Editing the IV changes ONLY block 1 — a common mistake is to edit the IV expecting a mid-message change.
- The scrambled-block garbage must not contain a quote/brace that breaks the surrounding parser.
- PKCS#7 on the last block: edits near the end can corrupt padding and cause a reject unrelated to your target field.

## Falsifier

Falsifier — the token is authenticated and any modification is rejected, or the parser rejects the inevitable garbage block: bit-flip survives neither.

## Cross-references

`cbc-padding-oracle.md` · `cbc-iv-equals-key.md` · `token-forgery-workflows.md`
