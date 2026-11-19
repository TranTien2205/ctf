# tcache entries[i] — the per-size head — deep

Companion to `the-entry-slot.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
