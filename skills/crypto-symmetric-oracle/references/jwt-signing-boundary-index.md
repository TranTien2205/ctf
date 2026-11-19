# Signed-token boundary — JWT, itsdangerous, Django — index

Signed tokens live at this class's boundary: the 'MAC' is HS256, but the
attack is usually algorithm confusion or a weak secret — not an oracle loop.

## Companions

- `jwt-signing-boundary-deep.md` — boundary conditions and the failure shape
- `jwt-signing-boundary-checklist.md` — the same content as an ordered checklist
- `jwt-signing-boundary-map.md` — the lookup table alone
- `../field-notes.md` — where outcomes land
