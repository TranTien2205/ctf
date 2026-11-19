# system + /bin/sh — the boring reliable end — deep

Companion to `system-binsh.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
