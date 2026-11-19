# Object-slot writes — vtables and handlers — deep

Companion to `fmtstr-write-obj-targets.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
