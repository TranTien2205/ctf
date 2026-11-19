# Leak then static — mixing leaked and fixed addresses — deep

Companion to `leak-then-static.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
