# Writing near environ — stack-reach via libc — deep

Companion to `the-environ-write.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
