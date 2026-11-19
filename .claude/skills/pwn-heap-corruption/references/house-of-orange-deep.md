# House of orange — top + FSOP composite — deep

Companion to `house-of-orange.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
