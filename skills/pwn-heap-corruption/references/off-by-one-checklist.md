# Off-by-one / off-by-NUL — the quiet overlap — checklist

Companion to `off-by-one.md`.

## Checklist

- [ ] 1. Chunk A (size 0x...8, P set) followed by chunk B.
- [ ] 2. Write A's buffer 1 byte too far → B's size LSB becomes 0x00.
- [ ] 3. B's size drops (e.g. 0x101 → 0x100); its P-bit may clear.
- [ ] 4. Free B: the allocator thinks B's predecessor (A's tail) is free →
- [ ] Needs a controllable next-chunk and a size where the low-byte change
- [ ] Alignment must keep the forged size sane.
