# tcache counts[] — the per-size tally — deep

Companion to `tcache-count.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
