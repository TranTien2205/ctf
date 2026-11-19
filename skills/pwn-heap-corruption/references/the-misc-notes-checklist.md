# Miscellaneous heap notes — checklist

Companion to `the-misc-notes.md`.

## Checklist

- [ ] mallopt knobs: M_MMAP_THRESHOLD, M_TRIM_THRESHOLD — tunable limits.
- [ ] The arena's mutex — threaded contention changes timing.
- [ ] usable_size vs request_size — the rounding gap.
- [ ] The minimum write — the smallest corruption that still lands.
- [ ] Chunk reuse after trim — top trimming returns memory to the OS.
