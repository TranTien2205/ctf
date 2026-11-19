# Mixed write widths — combining %hhn + %hn + %n — deep

Companion to `fmtstr-write-width-mix.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
