# The arena — malloc_state and its members — deep

Companion to `the-arena-struct.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
