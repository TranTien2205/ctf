# Verifying a bin poison — the two-malloc test — deep

Companion to `bin-poison-verify.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
