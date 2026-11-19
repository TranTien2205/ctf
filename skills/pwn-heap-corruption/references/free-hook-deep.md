# __free_hook/__malloc_hook — the removed shortcuts — deep

Companion to `free-hook.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
