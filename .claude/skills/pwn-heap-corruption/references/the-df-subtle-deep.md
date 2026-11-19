# The subtle double-free — via different paths — deep

Companion to `the-df-subtle.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
