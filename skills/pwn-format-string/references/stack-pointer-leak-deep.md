# Leaking a stack pointer — for ret-addr writes — deep

Companion to `stack-pointer-leak.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
