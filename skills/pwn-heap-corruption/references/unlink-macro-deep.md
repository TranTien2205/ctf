# The old unlink — pre-2.30 FD/BK write — deep

Companion to `unlink-macro.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
