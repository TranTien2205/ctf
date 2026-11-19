# The 0x7f alignment trick — fake chunk sizes — deep

Companion to `the-align-trick.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
