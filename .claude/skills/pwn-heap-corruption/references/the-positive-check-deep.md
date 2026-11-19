# Size positivity checks — can't be too small — deep

Companion to `the-positive-check.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
