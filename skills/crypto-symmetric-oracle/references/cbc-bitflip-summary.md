# CBC bit-flipping — targeted plaintext edits — summary

CBC decrypts block i as Dec(C_i) XOR C_{i-1}: flip a bit in C_{i-1} and the same bit flips in P_i while C_{i-1}'s own plaintext is scrambled. Controlled edits cost one block of garbage.

## Signal → route

- You need 'user' → 'admin' or a number changed in a CBC token → locate offset, flip bytes
- The token's IV is prepended and attacker-controlled → edit P_1 via IV
- Scrambled block must stay parseable → use IV or a don't-care block

## Falsifier

Falsifier — the token is authenticated and any modification is rejected, or the parser rejects the inevitable garbage block: bit-flip survives neither.
