# CBC bit-flipping — targeted plaintext edits — playbook

CBC decrypts block i as Dec(C_i) XOR C_{i-1}: flip a bit in C_{i-1} and the same bit flips in P_i while C_{i-1}'s own plaintext is scrambled. Controlled edits cost one block of garbage.

## Ordered playbook

1. Find which ciphertext block covers the target plaintext bytes (vary input, watch which block changes).
2. delta = P_want XOR P_have; xor delta into the PREVIOUS ciphertext block (or the IV for block 1).
3. The previous block decrypts to garbage — ensure it falls in a field the parser ignores.
4. If only the IV is malleable and you need a deeper block, chain: corrupt C_{i-1} to fix P_i while accepting garbage in P_{i-1}.

## Falsifier

Falsifier — the token is authenticated and any modification is rejected, or the parser rejects the inevitable garbage block: bit-flip survives neither.

## Commands

```bash
python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{'  # only for keystream reuse, not CBC
```
