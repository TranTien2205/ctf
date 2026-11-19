# The null byte — the chain's terminator


A 64-bit little-endian address's top bytes are zeros — a gets-style
read stops at the first \x00: the last address's high bytes truncate
the read — usually fine (the read ended anyway), but a mid-chain
zero in an address truncates early.

## The workaround

Gadgets with no zero bytes in their addresses; args computed (xor)
rather than literal; the terminator lands last.
