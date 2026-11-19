# Two frees, one chunk — the dup's anatomy — deep

Companion to `the-two-frees.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
