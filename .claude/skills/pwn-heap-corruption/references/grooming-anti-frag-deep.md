# Making grooming robust — determinism tricks — deep

Companion to `grooming-anti-frag.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
