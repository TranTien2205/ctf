# House of spirit — freeing a fake chunk — checklist

Companion to `house-of-spirit.md`.

## Checklist

- [ ] A fake chunk with a valid size and flags (aligned, P set, sane size).
- [ ] The NEXT chunk's size field must also look valid (checked on free).
- [ ] Write control over the memory you're fake-chunking.
- [ ] 1. Plant fake chunk A at address P: size field = S, and fake "next"
- [ ] 2. free(P) → P lands in the bin.
- [ ] 3. malloc(S-aligned) returns P → the alloc gives back your buffer.
