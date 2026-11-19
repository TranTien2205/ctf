# The heap summary — the one-page version

Version first, primitive second, leak before write, checks satisfied,
stages verified, target that fires. The allocator is the deputy; the
corruption is the instruction it obeys.

## The five lines

1. glibc version — names the technique space.
2. The bug — names the primitive.
3. The leaks — feed the aims.
4. The corruption — lands in a bin or a size field.
5. The write — lands on a firing slot.

Everything else is bookkeeping.

## The six gates

1. The bug reaches allocator state.
2. The version permits the technique.
3. The leaks feed the aim.
4. The checks on the path pass.
5. The write's target fires.
6. The flag reaches the hook.

Each gate falsifies a different route — the order of them is the order
of work.
