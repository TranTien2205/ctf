# Writing into .bss/.data — the static targets — deep

Companion to `fmtstr-and-bss.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
