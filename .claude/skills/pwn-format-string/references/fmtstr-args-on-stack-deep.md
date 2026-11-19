# Where the args actually sit — the stack picture — deep

Companion to `fmtstr-args-on-stack.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
