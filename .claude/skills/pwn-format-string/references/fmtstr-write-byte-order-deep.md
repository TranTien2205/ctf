# Byte-write ordering — low-to-high vs high-to-low — deep

Companion to `fmtstr-write-byte-order.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
