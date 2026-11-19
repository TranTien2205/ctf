# The verified run — the dry-run discipline — deep

Companion to `the-verified-run.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
