# Why heap corruption works — the theory — checklist

Companion to `heap-theory.md`.

## Checklist

- [ ] Size fields: believed → boundary confusion.
- [ ] fd/bk links: followed → the bin write.
- [ ] counts/keys: checked → the detection walls.
