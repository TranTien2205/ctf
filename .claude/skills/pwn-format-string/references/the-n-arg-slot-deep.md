# The %N$n arg slot — must hold a POINTER — deep

Companion to `the-n-arg-slot.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
