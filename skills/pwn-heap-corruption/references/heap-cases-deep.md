# Heap case studies — the shapes in the wild — deep

Companion to `heap-cases.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
