# Alloc-then-overflow — the boundary write — deep

Companion to `alloc-then-overflow.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
