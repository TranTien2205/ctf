# Free-anywhere — freeing a chosen address — checklist

Companion to `free-anywhere.md`.

## Checklist

- [ ] 1. Choose target T with a sane fake size field at T-8 (or forge it).
- [ ] 2. free(T) → T enters a bin.
- [ ] 3. malloc of matching size → returns T — your alloc's data writes into
