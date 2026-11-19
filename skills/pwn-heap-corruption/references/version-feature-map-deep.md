# The version feature map — what exists when — deep

Companion to `version-feature-map.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
