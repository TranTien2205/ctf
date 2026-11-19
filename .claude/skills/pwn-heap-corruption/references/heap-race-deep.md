# Heap and threads — race-window corruption — deep

Companion to `heap-race.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
