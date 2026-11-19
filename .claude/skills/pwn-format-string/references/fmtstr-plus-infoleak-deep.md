# Fmtstr + separate info-leak — two primitives, one chain — deep

Companion to `fmtstr-plus-infoleak.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
