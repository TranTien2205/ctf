# Reading the top — the heap's end pointer — checklist

Companion to `the-top-leak.md`.

## Checklist

- [ ] top's value = heap_base + heap_size → names the heap's extent.
- [ ] top-adjacent allocs are the wilderness — corruption of top's size is
