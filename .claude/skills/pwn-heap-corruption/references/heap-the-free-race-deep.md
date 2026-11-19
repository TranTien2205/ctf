# The free race — ordering the corruption — deep

Companion to `heap-the-free-race.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
