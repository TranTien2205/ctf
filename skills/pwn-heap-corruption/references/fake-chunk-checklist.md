# Fake chunks — planting allocator-shaped data — checklist

Companion to `fake-chunk.md`.

## Checklist

- [ ] Aligned address (0x10).
- [ ] size field: sane size | P set.
- [ ] The "next" chunk's size (at fake + size): any non-zero sane value —
- [ ] 1. Write the fake metadata into controllable memory.
- [ ] 2. free(&fake_user_area) or aim a bin fd at it.
- [ ] 3. The allocator returns/manages your memory — writes land in your
