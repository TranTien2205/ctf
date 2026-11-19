# The arena — malloc_state and its members — checklist

Companion to `the-arena-struct.md`.

## Checklist

- [ ] fastbinsY[NFASTBINS] — the fastbin heads.
- [ ] bins[] — unsorted + small + large bin heads (the leak's target).
- [ ] top — the wilderness pointer.
- [ ] next — the arena chain.
