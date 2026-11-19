# Heap write targets — where the aim lands — deep

Companion to `write-targets-heap.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
