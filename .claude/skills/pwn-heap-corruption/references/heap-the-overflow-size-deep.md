# The overflow's size class — which chunk — deep

Companion to `heap-the-overflow-size.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
