# Coalescing order — which neighbor merges first — deep

Companion to `coalesce-order.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
