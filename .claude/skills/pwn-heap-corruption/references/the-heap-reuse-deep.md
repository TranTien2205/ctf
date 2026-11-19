# The reuse window — when a freed chunk returns — deep

Companion to `the-heap-reuse.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
