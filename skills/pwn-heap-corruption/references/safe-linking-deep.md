# Safe-linking — the fd mangling (glibc 2.32+) — deep

Companion to `safe-linking.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
