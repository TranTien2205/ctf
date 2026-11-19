# Locating the tcache key field — deep

Companion to `the-key-offset.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
