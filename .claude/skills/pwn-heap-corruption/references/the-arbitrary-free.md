# Arbitrary-free — freeing where you choose


An OOB index or a corruptible pointer field lets free() run on an
arbitrary address — the freed region joins a bin, allocs return it.

## Steps

1. Find the free-anywhere path (OOB delete, forged ptr field).
2. Prepare the target region: forge a fake chunk's size + next-size.
3. free(target) → bin; malloc → target returned.

## Falsifier

The free path validates the pointer (alignment, range): arbitrary-free
is checked — fake within the allowed window.
