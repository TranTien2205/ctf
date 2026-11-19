# A-B-A vs A-A — the ordering detail — deep

Companion to `the-double-order.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
