# Fake chunks — planting allocator-shaped data


A fake chunk is attacker memory formatted to satisfy free()/malloc
checks: right size, plausible flags, a sane next-size — the allocator
treats your buffer as a real chunk.

## Minimum requirements (x64)

- Aligned address (0x10).
- size field: sane size | P set.
- The "next" chunk's size (at fake + size): any non-zero sane value —
  checked on free in most versions.

## Steps

1. Write the fake metadata into controllable memory.
2. free(&fake_user_area) or aim a bin fd at it.
3. The allocator returns/manages your memory — writes land in your
   buffer.

## Falsifier

The sanity checks reject the fake (size mismatch vs bin, bad next-size):
tighten the forged fields to satisfy THIS version's checks.
