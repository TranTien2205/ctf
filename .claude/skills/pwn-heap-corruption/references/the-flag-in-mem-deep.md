# Flag-in-memory — reading it off the heap — deep

Companion to `the-flag-in-mem.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
