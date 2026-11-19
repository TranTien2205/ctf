# Overlapping chunks — the goal of most grooming — deep

Companion to `overlapping-chunks.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
