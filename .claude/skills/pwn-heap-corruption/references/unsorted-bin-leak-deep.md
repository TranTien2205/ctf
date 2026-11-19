# The unsorted-bin leak — libc for free — deep

Companion to `unsorted-bin-leak.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
