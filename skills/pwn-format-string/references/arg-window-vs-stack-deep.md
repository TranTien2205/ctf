# The arg window vs raw stack — what %N$p actually sees — deep

Companion to `arg-window-vs-stack.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
