# The grooming flow — alloc/free as bytecode — deep

Companion to `heap-grooming-flow.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
