# The dangling arg — reading a stale pointer — deep

Companion to `fmtstr-dangling-arg.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
