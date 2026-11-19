# Read shapes — what the leak channel returns — deep

Companion to `the-read-shape.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
