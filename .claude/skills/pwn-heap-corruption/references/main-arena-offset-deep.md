# main_arena — where it sits in libc — deep

Companion to `main-arena-offset.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
