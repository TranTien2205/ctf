# House of mind — arena redirection — checklist

Companion to `house-of-mind.md`.

## Checklist

- [ ] 1. Set the victim chunk's N bit (size | 4).
- [ ] 2. Compute heap_info_for from the chunk address → point it at a fake
- [ ] 3. free() routes the chunk into your fake arena's bins.
- [ ] 4. Allocations from that arena return your planted chunks.
- [ ] Needs substantial fake-structure setup in writable memory.
- [ ] The arena arithmetic is version-sensitive.
