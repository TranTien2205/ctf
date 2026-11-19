# Heap boundaries — where the class ends — deep

Companion to `heap-the-boundaries.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
