# House of force — top-chunk size corruption — deep

Companion to `house-of-force.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
