# The bk pointer — largebin's second link — checklist

Companion to `the-bk-only.md`.

## Checklist

- [ ] bk->fd = victim writes on unlink — one direction.
- [ ] bk_nextsize corruption — the largebin write.
- [ ] A fake bk pointing into your data makes the unlink write INTO your
