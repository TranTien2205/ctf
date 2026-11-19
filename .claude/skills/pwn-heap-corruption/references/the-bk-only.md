# The bk pointer — largebin's second link


Smallbin/largebin chunks carry bk — doubly-linked lists let the walk go
both ways; corrupting bk gives different write shapes than fd.

## Use

- bk->fd = victim writes on unlink — one direction.
- bk_nextsize corruption — the largebin write.
- A fake bk pointing into your data makes the unlink write INTO your
  buffer.

## Falsifier

The consistency check (bk->fd == chunk) rejects the forged link:
modern unlink needs both links self-consistent.
