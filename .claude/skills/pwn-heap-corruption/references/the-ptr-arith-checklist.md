# Pointer arithmetic for aims — the offsets — checklist

Companion to `the-ptr-arith.md`.

## Checklist

- [ ] fd aim at T: write (pos>>12) ^ T at chunk+0.
- [ ] largebin bk_nextsize aim: target - 0x20.
- [ ] fake chunk free: pass P+0x10, header at P.
- [ ] unsorted bk aim: target - 0x10.
- [ ] hook: exactly the symbol address.
- [ ] ret-addr slot: the leaked stack ptr ± frame delta.
