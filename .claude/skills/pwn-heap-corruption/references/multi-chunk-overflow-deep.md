# Overflow spanning several chunks — deep

Companion to `multi-chunk-overflow.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
