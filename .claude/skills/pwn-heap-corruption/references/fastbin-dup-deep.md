# Fastbin dup — the A-B-A double free — deep

Companion to `fastbin-dup.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
