# Many-chunk overflows — the wide corruption — deep

Companion to `heap-the-many.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
