# First-fit and bin order — where allocs come from — deep

Companion to `first-fit.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
