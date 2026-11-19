# The consolidation window — the timing — deep

Companion to `the-consolidate-window.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
