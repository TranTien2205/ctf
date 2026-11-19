# The object table — tracking slots across ops — deep

Companion to `the-object-table.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
