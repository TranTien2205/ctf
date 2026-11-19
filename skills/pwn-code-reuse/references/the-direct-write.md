# The direct write — no chain needed


When the bug is already an arbitrary write (fmtstr %n, a heap write):
the chain's work is the write itself — the "gadgets" are the pointer
targets.

## The crossover

pwn-format-string and pwn-heap-corruption reach code-reuse when the
write aims at a call slot — the chain then is just the target address.
