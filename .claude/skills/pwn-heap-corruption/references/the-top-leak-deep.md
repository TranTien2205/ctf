# Reading the top — the heap's end pointer — deep

Companion to `the-top-leak.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
