# _IO_vtable_check — the FSOP gauntlet — deep

Companion to `vtable-check.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
