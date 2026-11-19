# CMAC, OMAC, and the MAC-variant zoo — index

CBC-MAC's variable-length forgery was fixed by CMAC/OMAC: the last block is
XOR'd with a derived subkey before encryption, which kills the simple
splice. Naming the construction correctly is the whole game.

## Companions

- `cmac-and-variants-deep.md` — boundary conditions and the failure shape
- `cmac-and-variants-checklist.md` — the same content as an ordered checklist
- `cmac-and-variants-map.md` — the lookup table alone
- `../field-notes.md` — where outcomes land
