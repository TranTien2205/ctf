# CBC bit-flipping — targeted plaintext edits — index

CBC decrypts block i as Dec(C_i) XOR C_{i-1}: flip a bit in C_{i-1} and the same bit flips in P_i while C_{i-1}'s own plaintext is scrambled. Controlled edits cost one block of garbage.

## Related modules

- `cbc-bitflip-deep.md` — mechanism internals and boundary conditions
- `cbc-bitflip-variant.md` — when the surface shape changes
- `cbc-bitflip-checklist.md` — the ordered operational steps
- `cbc-bitflip-catalogue.md` — case enumeration

## Cross-references

`cbc-padding-oracle.md` · `cbc-iv-equals-key.md` · `token-forgery-workflows.md`
