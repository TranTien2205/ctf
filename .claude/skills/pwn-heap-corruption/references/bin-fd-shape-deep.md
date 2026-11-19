# The fd's shape — what a bin link looks like — deep

Companion to `bin-fd-shape.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
