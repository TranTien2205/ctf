# Fmtstr on a heap buffer — where the args point — deep

Companion to `fmtstr-on-heap-buf.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
