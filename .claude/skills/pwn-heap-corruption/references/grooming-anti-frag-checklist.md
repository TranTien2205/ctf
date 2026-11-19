# Making grooming robust — determinism tricks — checklist

Companion to `grooming-anti-frag.md`.

## Checklist

- [ ] Spray a known number of filler allocs to reach a deterministic bin
- [ ] Free in a fixed pattern; allocate guards to fence the layout.
- [ ] Use a fresh connection where the heap is predictable (early
- [ ] Consume the "unknown" frees first so later state is deterministic.
