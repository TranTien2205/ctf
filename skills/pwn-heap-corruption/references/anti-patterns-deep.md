# Heap anti-patterns — the ways runs go wrong — deep

Companion to `anti-patterns.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
