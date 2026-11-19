# The full trap list — every way heap runs die — deep

Companion to `the-trap-list.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
