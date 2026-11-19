# Fmtstr in a recursive function — deep

Companion to `fmtstr-recursion.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
