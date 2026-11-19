# Where the flag lives — targeting the final read — deep

Companion to `the-flag-loc.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
