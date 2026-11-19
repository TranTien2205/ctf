# The free race — ordering the corruption — checklist

Companion to `heap-the-free-race.md`.

## Checklist

- [ ] free() writes fd/key into the chunk — YOUR write must come after.
- [ ] A second alloc returns the chunk — your stale write is overwritten.
