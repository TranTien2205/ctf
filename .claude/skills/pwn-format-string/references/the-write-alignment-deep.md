# Write alignment — the pointer must be arg-aligned — deep

Companion to `the-write-alignment.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
