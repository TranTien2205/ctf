# The heap header — heap_info on thread arenas — deep

Companion to `the-heap-header.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
