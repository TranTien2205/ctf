# Fmtstr under PIE — every address needs the base — deep

Companion to `fmtstr-under-pie.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
