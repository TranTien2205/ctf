# Reading the GOT — the leak's target


A GOT entry's contents = the resolved function's address — read it
by calling puts(got[x]) or write(1, got[x], 8).

## The timing

Read it AFTER the function's been called — a lazy-binding GOT entry
holds a resolver address, not libc's.
