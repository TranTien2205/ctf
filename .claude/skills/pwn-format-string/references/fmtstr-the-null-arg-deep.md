# The null-arg edge — %s on a null pointer — deep

Companion to `fmtstr-the-null-arg.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
