# GOT under PIE — the slot address is base+offset — deep

Companion to `fmtstr-pie-got.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
