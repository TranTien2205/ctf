# Where a stack address comes from — the leak sources — deep

Companion to `fmtstr-stack-addr-source.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
