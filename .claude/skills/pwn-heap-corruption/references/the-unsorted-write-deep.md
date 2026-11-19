# Unsorted-bin writes — limited but leak-free — deep

Companion to `the-unsorted-write.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
