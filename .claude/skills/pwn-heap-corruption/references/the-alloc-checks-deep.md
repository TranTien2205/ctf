# malloc() checks — the gates on allocation — deep

Companion to `the-alloc-checks.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
