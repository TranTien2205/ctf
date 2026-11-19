# Format-string length limits — fitting the payload — deep

Companion to `fmtstr-length-limit.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
