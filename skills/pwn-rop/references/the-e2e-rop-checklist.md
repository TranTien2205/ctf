# End to end — a worked ROP run — checklist

Companion to `the-e2e-rop.md`.

## Checklist

- [ ] 1. Offset 72 (cyclic).
- [ ] 2. pop_rdi at 0x401236 (/R).
- [ ] 3. got_puts 0x404018, plt_puts 0x401030 (readelf -r + pdf).
- [ ] 4. main 0x4011c0 (afl).
- [ ] 5. Stage1 fires; the print gives 0x7f12... — libc base computed.
- [ ] 6. Stage2: pop_rdi + binsh + ret + system → shell.
- [ ] 7. cat flag → the hook.
