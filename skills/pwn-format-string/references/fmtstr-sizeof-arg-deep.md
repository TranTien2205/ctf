# The arg-size edge — %ln vs %n on x32 — deep

Companion to `fmtstr-sizeof-arg.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
