# The first ten minutes — the heap run — deep

Companion to `heap-the-first-ten.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
