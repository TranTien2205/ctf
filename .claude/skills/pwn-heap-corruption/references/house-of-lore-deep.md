# House of lore — smallbin recursive insert — deep

Companion to `house-of-lore.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
