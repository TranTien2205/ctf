# Bug-to-technique matrix — which recipe fits which bug — deep

Companion to `primitive-matrix.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
