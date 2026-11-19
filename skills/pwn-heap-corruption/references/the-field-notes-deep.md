# Heap field notes — recording the run — deep

Companion to `the-field-notes.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
