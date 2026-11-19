# The unsorted sort pass — where chunks get classified — deep

Companion to `the-sort-pass.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
