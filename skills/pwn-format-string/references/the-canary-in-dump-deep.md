# Finding the canary in a %p dump — deep

Companion to `the-canary-in-dump.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
