# Leaking libc — the GOT-read path — deep

Companion to `fmtstr-libc-leak.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
