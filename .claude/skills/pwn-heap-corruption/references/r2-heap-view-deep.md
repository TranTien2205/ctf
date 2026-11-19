# r2 -d heap view — dmh and friends — deep

Companion to `r2-heap-view.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
