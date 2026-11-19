# CBC bit-flipping — targeted plaintext edits

CBC decrypts block i as Dec(C_i) XOR C_{i-1}: flip a bit in C_{i-1} and the same bit flips in P_i while C_{i-1}'s own plaintext is scrambled. Controlled edits cost one block of garbage.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| You need 'user' → 'admin' or a number changed in a CBC token | bit-flip applies | locate offset, flip bytes |
| The token's IV is prepended and attacker-controlled | first block is fully controllable | edit P_1 via IV |
| Scrambled block must stay parseable | needs structure tolerant to garbage | use IV or a don't-care block |

## Steps

1. Find which ciphertext block covers the target plaintext bytes (vary input, watch which block changes).
2. delta = P_want XOR P_have; xor delta into the PREVIOUS ciphertext block (or the IV for block 1).
3. The previous block decrypts to garbage — ensure it falls in a field the parser ignores.
4. If only the IV is malleable and you need a deeper block, chain: corrupt C_{i-1} to fix P_i while accepting garbage in P_{i-1}.

## Falsifier

Falsifier — the token is authenticated and any modification is rejected, or the parser rejects the inevitable garbage block: bit-flip survives neither.

## Traps

- Editing the IV changes ONLY block 1 — a common mistake is to edit the IV expecting a mid-message change.
- The scrambled-block garbage must not contain a quote/brace that breaks the surrounding parser.
- PKCS#7 on the last block: edits near the end can corrupt padding and cause a reject unrelated to your target field.
- Some tokens prefix a length or CRC; the CRC block scrambles too and must be recomputed or bypassed.

## Commands

```bash
python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{'  # only for keystream reuse, not CBC
```

## Cross-references

`cbc-padding-oracle.md` · `cbc-iv-equals-key.md` · `token-forgery-workflows.md`
