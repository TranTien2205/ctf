# The print-object op — blessed leaks — deep

Companion to `the-object-print.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
