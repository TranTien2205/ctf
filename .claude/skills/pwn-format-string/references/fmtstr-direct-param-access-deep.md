# Direct parameter access — %N$x semantics — deep

Companion to `fmtstr-direct-param-access.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
