# The null-pointer write — writing at 0 — deep

Companion to `the-null-safe.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
