# printf-family and the heap — stderr FILEs — deep

Companion to `the-printf-family.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
