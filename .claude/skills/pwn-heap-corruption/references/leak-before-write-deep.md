# Leak before write — the order that survives versions — deep

Companion to `leak-before-write.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
