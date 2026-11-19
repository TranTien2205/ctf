# The chain card — recording the solved heap — deep

Companion to `heap-the-chain-card.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
