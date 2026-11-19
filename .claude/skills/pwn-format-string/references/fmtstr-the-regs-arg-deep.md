# Register args as leak sources — rsi..r9 values — deep

Companion to `fmtstr-the-regs-arg.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
