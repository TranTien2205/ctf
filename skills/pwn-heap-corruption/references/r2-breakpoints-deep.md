# Breakpoint strategy — where to pause — deep

Companion to `r2-breakpoints.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
