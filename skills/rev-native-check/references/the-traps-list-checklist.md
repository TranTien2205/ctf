# The traps — the common walls — checklist

Companion to `the-traps-list.md`.

## Checklist

- [ ] strings misses built strings — read the mov-sequence.
- [ ] The stored side isn't a C string — read n bytes, not a ps.
- [ ] The transform is two-stage — replicate BOTH stages.
- [ ] The compare uses a swapped operand order — check which side is
- [ ] ASLR moves the addresses — use offsets under r2.
- [ ] A second check guards the real flag — peel both.
