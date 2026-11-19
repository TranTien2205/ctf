# The glibc version question — before any technique — deep

Companion to `glibc-version-first.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
