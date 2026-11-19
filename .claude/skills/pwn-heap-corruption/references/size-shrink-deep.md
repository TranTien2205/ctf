# The size-shrink overlap — free bigger, alloc smaller — deep

Companion to `size-shrink.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
