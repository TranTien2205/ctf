# Alignment checks — where they catch you


free() requires an aligned pointer (0x10 x64): unaligned → "free():
invalid pointer". Every fake chunk must sit on a boundary.

## The math

- The pointer passed to free must be chunk_addr + 0x10 (the user area)
  — fake-chunk recipes pass &fake_data, the allocator reads the header
  at &fake_data - 0x10.
- Aiming a bin at a misaligned target: the return is still aligned-
  interpreted — the size field at target-0x10 must exist and be sane.

## Falsifier

The target you need can't sit at an aligned address with a sane
preceding size field: the alignment check closes that aim.
