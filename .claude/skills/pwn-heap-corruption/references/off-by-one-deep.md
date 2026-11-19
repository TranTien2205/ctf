# Off-by-one / off-by-NUL — the quiet overlap — deep

Companion to `off-by-one.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
