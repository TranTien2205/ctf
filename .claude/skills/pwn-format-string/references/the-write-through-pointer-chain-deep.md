# The write-through-pointer-chain — *ptr where ptr is controlled — deep

Companion to `the-write-through-pointer-chain.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
