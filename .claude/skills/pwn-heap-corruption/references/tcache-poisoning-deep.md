# Tcache poisoning — aiming the fd pointer — deep

Companion to `tcache-poisoning.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
