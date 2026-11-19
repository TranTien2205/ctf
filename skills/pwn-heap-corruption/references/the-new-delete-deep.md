# new/delete — the C++ operators — deep

Companion to `the-new-delete.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
