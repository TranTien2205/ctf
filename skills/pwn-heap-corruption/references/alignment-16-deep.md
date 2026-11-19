# The 0x10 alignment — size classes on x64 — deep

Companion to `alignment-16.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
