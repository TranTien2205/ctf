# The blind leak via a side channel — deep

Companion to `the-blind-leak-via-side.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
