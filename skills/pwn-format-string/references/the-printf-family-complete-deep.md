# The complete printf family — every call that takes a format — deep

Companion to `the-printf-family-complete.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
