# Smallbin's double-link check — 2.30+ — deep

Companion to `the-smallbin-check.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
