# The add op — allocation as a tool — deep

Companion to `the-add-op.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
