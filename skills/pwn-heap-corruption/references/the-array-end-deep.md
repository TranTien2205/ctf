# Past the pointer array — the OOB read/write — deep

Companion to `the-array-end.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
