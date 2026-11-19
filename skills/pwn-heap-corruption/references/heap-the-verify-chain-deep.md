# The verify chain — every stage's check — deep

Companion to `heap-the-verify-chain.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
