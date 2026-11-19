# free() checks — the gates on deallocation — deep

Companion to `the-free-checks.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
