# Large-bin attack — the size-sorted write — checklist

Companion to `large-bin-attack.md`.

## Checklist

- [ ] 1. Two large chunks: a victim in the large bin and one to insert.
- [ ] 2. Corrupt victim->bk_nextsize = target - 0x20 (x64).
- [ ] 3. Force an insertion that walks past the victim.
- [ ] 4. A pointer-sized value (the chunk address) lands at target.
