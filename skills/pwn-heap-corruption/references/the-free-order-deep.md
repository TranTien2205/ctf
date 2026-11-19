# The free order — sequencing the corruption — deep

Companion to `the-free-order.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
