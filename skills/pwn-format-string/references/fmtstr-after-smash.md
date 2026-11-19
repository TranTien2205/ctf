# Fmtstr after a smash — when it's the second primitive


Sometimes the format call happens AFTER a stack overflow already ran:
the smash corrupted state, the fmtstr finishes — or the smash's data
lands as a format arg.

## Steps

1. A smash that writes %p/%n specifiers into the buffer later printf'd:
   the fmtstr payload rides the overflow.
2. Or the smash corrupts a pointer the printf reads.
3. Both primitives in one run — the smash's data IS the format.

## Falsifier

The printf runs before any overflow, or on different data: disjoint
primitives.
