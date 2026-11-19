# Null bytes inside the fmtstr input — deep

Companion to `fmtstr-arg-nulls.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
