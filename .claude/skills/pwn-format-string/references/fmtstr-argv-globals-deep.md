# argv/env strings as write targets — deep

Companion to `fmtstr-argv-globals.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
