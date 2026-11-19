# Writing the return address via %n — the details — checklist

Companion to `write-into-ret.md`.

## Checklist

- [ ] 1. Dump %p — find a stack-pointer-shaped word (0x7ff...).
- [ ] 2. It's rbp of some frame — the saved return sits at rbp+8.
- [ ] 3. Plant rbp+8 as the %N$n argument; write the target address byte-wise.
- [ ] 4. On return, RIP = your value.
- [ ] Frame-pointer omission (-fomit-frame-pointer) breaks the rbp chain —
- [ ] Stack addresses are ASLR'd — must be leaked each run.
