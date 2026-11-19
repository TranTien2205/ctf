# Free-anywhere — freeing a chosen address — deep

Companion to `free-anywhere.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
