# Stack vs heap fmt buffer — where the input sits — checklist

Companion to `fmtstr-stack-vs-heap.md`.

## Checklist

- [ ] 1. Stack buffer: your bytes appear in the dump (the marker test).
- [ ] 2. Heap buffer: not an arg — %N$p can't reach your input.
- [ ] 3. The primitive still reads/writes args — just not via planted input.
- [ ] 4. Plant via an existing arg or a prior write.
