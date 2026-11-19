# Always unsorted-leak first — the cheapest stage — deep

Companion to `the-unsorted-first.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
