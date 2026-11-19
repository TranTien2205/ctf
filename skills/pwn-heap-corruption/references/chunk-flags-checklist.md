# N/M/P — the size-field flags — checklist

Companion to `chunk-flags.md`.

## Checklist

- [ ] P (0x01): the PREVIOUS chunk is in use — when clear, prev_size is
- [ ] M (0x02): mmap'd chunk — not heap-resident.
- [ ] N (0x04): non-main arena — belongs to a thread arena.
- [ ] Clearing P (off-by-NUL) activates prev_size → consolidation eats a
- [ ] Setting N misdirects free() to a fake arena (house of mind).
- [ ] M is checked before unlink paths.
