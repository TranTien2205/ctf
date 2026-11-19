# House of roman — fastbin to __malloc_hook — deep

Companion to `house-of-roman.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
