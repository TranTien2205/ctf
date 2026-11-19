# The arg consumption — how specifiers walk the args — deep

Companion to `the-arg-consumption.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
