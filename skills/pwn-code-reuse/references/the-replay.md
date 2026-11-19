# The replay — running it back


A working chain should replay: same input, same flag — if it doesn't,
something's nondeterministic (ASLR, a race, a heap layout) — find the
variable.
