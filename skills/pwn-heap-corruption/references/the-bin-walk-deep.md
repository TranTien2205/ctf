# Walking a bin — following the links — deep

Companion to `the-bin-walk.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
