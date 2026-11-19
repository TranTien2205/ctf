# fd/bk offsets in the user area — x64 map — deep

Companion to `the-link-field-offset.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
