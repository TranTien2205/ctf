# Partial success — when half the chain works — deep

Companion to `heap-the-partial.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
