# The very first check — does the class apply? — deep

Companion to `heap-first-check.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
