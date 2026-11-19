# The order of work — the exploit's outline — deep

Companion to `the-order-of-work.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
