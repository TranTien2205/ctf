# Verifying order assumptions — first-fit — deep

Companion to `heap-the-order-verify.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
