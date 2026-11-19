# The %N$n arg slot — must hold a POINTER


The Nth argument must CONTAIN a pointer to the write target — not the
target value itself. If your input bytes form the pointer, they must
land exactly on an arg boundary.

## Steps

1. The arg slot must contain the target's ADDRESS, 8-byte aligned on x64.
2. If your input's bytes form the pointer, align them to the boundary.
3. A 4-byte-misaligned pointer writes to the wrong address.

## Falsifier

No arg position can hold your full pointer value: the write destination
isn't selectable.
