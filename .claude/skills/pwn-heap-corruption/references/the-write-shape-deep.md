# Write shapes — byte/word/page granularity — deep

Companion to `the-write-shape.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
