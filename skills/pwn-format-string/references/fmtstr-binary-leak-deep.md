# Leaking the binary base — the PIE de-randomization — deep

Companion to `fmtstr-binary-leak.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
