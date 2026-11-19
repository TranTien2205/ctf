# Confirming partial RELRO before the GOT write — deep

Companion to `fmtstr-partial-relro-check.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
