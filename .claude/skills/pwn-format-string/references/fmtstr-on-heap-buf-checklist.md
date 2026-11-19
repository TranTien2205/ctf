# Fmtstr on a heap buffer — where the args point — checklist

Companion to `fmtstr-on-heap-buf.md`.

## Checklist

- [ ] 1. A heap buffer isn't a stack argument — %N$p won't see your bytes.
- [ ] 2. The primitive still reads/writes stack args — you just can't plant
- [ ] 3. Plant the pointer via a first write, or use an existing arg.
