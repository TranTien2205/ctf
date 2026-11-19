# Offset stability — does N survive across calls? — deep

Companion to `fmtstr-stability.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
