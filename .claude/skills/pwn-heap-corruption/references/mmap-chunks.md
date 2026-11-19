# Mmap'd chunks — outside the heap


Huge requests (> mmap_threshold, ~128KB) mmap directly — no heap
metadata, no bins, M flag set; free is munmap.

## Consequences

- No heap corruption applies — no fd/bk to poison.
- An overflow into an mmap'd chunk hits unmapped memory — crash, not
  control.
- The M bit in the size field identifies one.

## Falsifier

The target object is mmap'd: heap techniques don't reach it.
