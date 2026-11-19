# fd_nextsize/bk_nextsize — the largebin extras — deep

Companion to `the-nextsize-fields.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
