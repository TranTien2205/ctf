# Sanitizer strips — when % is filtered — deep

Companion to `fmtstr-sanitize-strip.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
