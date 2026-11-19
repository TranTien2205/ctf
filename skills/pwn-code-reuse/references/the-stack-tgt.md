# The stack target — aiming at stack memory


Writing to the stack: needs a stack-pointer leak — the stack's address
isn't fixed under ASLR.

## The leak

saved rbp or a libc env pointer gives a stack address to aim at.
