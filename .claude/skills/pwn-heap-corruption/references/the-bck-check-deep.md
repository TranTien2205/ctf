# The bck->fd check — unsorted's consistency — deep

Companion to `the-bck-check.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
