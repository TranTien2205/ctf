# How many writes — the primitive's cost — checklist

Companion to `the-write-count.md`.

## Checklist

- [ ] tcache poison (post-2.32): 1 leak-read + 1 fd write + 2 allocs + 1
- [ ] unsorted leak: 1 free + 1 dangling read.
- [ ] fastbin dup: 3 frees + 3 allocs.
- [ ] off-by-one overlap: 1 byte + 1 free + 1 realloc.
