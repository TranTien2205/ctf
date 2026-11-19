# The loop service — multi-call exploitation — deep

Companion to `fmtstr-loop-service.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
