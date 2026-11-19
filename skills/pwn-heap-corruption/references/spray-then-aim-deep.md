# Spray-then-aim — the imprecise fallback — deep

Companion to `spray-then-aim.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
