# The slot cap — the op budget's ceiling — deep

Companion to `the-array-cap.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
