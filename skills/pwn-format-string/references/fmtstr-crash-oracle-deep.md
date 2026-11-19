# The crash oracle — when output never returns — deep

Companion to `fmtstr-crash-oracle.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
