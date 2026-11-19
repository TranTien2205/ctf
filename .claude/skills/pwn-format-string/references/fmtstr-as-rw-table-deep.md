# The fmtstr read/write table — the complete primitive set — deep

Companion to `fmtstr-as-rw-table.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
