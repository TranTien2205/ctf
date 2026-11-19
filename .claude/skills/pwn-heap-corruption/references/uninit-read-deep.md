# Uninitialized chunk read — stale data leaks — deep

Companion to `uninit-read.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
