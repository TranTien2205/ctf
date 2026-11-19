# The stack print order — what %p.%p.%p reveals — deep

Companion to `fmtstr-stack-print-order.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
