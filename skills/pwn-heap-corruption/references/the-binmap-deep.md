# binmap — the arena's occupancy bitmap — deep

Companion to `the-binmap.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
