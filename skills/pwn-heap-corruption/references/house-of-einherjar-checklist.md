# House of einherjar — null-byte consolidation — checklist

Companion to `house-of-einherjar.md`.

## Checklist

- [ ] 1. Chunk A, then B. Overflow A's last byte → B's P clears, prev_size
- [ ] 2. Plant a fake chunk at B - prev_size (inside your own data).
- [ ] 3. free(B) → consolidate backward to the fake chunk.
- [ ] 4. The merged region spans your fake chunk → the next alloc returns it.
- [ ] An off-by-one into B's size/prev_size.
- [ ] A fake chunk whose P-bit and size satisfy the unlink checks.
- [ ] Post-2.30 unlink hardening means the fake chunk's fd/bk must be
