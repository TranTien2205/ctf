# The 0x8 alignment — x86 chunk sizes — deep

Companion to `alignment-x86.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
