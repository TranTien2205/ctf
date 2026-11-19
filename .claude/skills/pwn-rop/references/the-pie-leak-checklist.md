# PIE — the code-pointer leak — checklist

Companion to `the-pie-leak.md`.

## Checklist

- [ ] A return address on the stack (read via fmtstr or a print).
- [ ] A saved code pointer in a readable structure.
- [ ] The binary's own output of an address.
