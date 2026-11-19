# tcache_perthread_struct — the per-thread control — deep

Companion to `the-tcache-struct.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
