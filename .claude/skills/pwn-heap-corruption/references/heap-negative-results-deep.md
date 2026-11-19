# Heap negative results — the kill map — deep

Companion to `heap-negative-results.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
