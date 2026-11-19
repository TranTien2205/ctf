# _IO_list_all — the FILE chain head — deep

Companion to `io-list-all.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
