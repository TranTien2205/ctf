# ROP + heap — the write's landing — checklist

Companion to `the-heap-combo.md`.

## Checklist

- [ ] 1. Heap write → the chain's bytes at a known heap address.
- [ ] 2. A pivot gadget (xchg rsp, reg or leave;ret) moves rsp there.
- [ ] 3. The chain runs.
