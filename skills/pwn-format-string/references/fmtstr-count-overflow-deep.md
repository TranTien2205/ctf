# Count overflow — when the byte-count wraps — deep

Companion to `fmtstr-count-overflow.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
