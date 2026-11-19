# The one-gadget — the execve constraint gadget — deep

Companion to `one-gadget.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
