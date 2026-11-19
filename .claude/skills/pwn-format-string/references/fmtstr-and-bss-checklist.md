# Writing into .bss/.data — the static targets — checklist

Companion to `fmtstr-and-bss.md`.

## Checklist

- [ ] 1. Under non-PIE, .bss/.data addresses are compile-time fixed.
- [ ] 2. Global flags, string pointers, sizes — overwrite directly.
- [ ] 3. A global function pointer is a redirect target too.
- [ ] 4. Read the symbol table for globals: nm ./chal or r2's is.
