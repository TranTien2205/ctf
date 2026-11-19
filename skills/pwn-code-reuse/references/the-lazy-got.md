# The lazy GOT — resolver stubs


Before first call, GOT[x] holds a resolver address — a binary/ld
address, not the libc function: the read gives the wrong thing.

## The rule

Read a GOT entry only AFTER the function's been called — or read a
naturally-resolved entry.
