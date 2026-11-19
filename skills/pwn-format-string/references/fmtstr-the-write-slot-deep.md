# Choosing the slot — GOT vs ret vs hook decision — deep

Companion to `fmtstr-the-write-slot.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
