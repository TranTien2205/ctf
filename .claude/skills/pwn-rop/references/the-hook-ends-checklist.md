# The hook endings — __free_hook/__malloc_hook — checklist

Companion to `the-hook-ends.md`.

## Checklist

- [ ] A libc leak (the hook's address).
- [ ] An arbitrary write.
- [ ] A free() call by the program (or a chain call to free).
