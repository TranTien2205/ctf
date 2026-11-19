# exit handlers and __run_exit_handlers — deep

Companion to `exit-handlers.md`.

Heap corruption is relational: the bug edits allocator state and the allocator's own machinery delivers the write on a later op. Everything is version-keyed to glibc.
