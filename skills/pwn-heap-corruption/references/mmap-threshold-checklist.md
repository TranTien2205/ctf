# The mmap threshold — where heap ends — checklist

Companion to `mmap-threshold.md`.

## Checklist

- [ ] First huge alloc mmaps; freeing it may RAISE the threshold —
- [ ] dm maps show which region an address sits in.
- [ ] Force huge allocs to isolate objects (spray separation).
- [ ] A free that lifts the threshold changes later routing.
