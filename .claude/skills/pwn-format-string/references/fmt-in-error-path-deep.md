# Fmtstr in error paths — the handler case — deep

Companion to `fmt-in-error-path.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
