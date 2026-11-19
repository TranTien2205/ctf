# bins[] inside the arena — the unsorted head — deep

Companion to `the-arena-bins.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
