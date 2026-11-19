# 32-bit fmtstr — the x86 shape — deep

Companion to `fmtstr-32-bit.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
