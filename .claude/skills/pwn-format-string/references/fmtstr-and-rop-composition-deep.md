# Fmtstr + ROP — the write that feeds the chain — deep

Companion to `fmtstr-and-rop-composition.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
