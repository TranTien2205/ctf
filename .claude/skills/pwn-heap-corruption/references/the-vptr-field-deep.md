# The vptr — the C++ object's first field — deep

Companion to `the-vptr-field.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
