# Heap vs loader regions — address geography — checklist

Companion to `the-heap-vs-ld.md`.

## Checklist

- [ ] 0x55/0x56.. → PIE binary or main-arena-relative heap.
- [ ] 0x7f.. mid → libc/ld mappings.
- [ ] 0x7ff.. high → stack.
- [ ] Small ints → counts/sizes, not pointers.
