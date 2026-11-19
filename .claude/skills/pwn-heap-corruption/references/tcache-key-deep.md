# The tcache key — 2.29+ double-free detection — deep

Companion to `tcache-key.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
