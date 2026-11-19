# A complete modern chain — 2.32+ end to end — deep

Companion to `heap-full-chain.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
