# The format-in-the-buffer — the primitive is that buf IS the format — deep

Companion to `the-format-in-the-buffer.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
