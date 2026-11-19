# The null-byte boundary — off-by-null precisely — deep

Companion to `the-null-trick.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
