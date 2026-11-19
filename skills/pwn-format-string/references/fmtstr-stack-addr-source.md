# Where a stack address comes from — the leak sources


A %n ret-addr write needs a stack address. Sources: a saved rbp in the
%p dump, an argv/env pointer, or a stack-arg backpointer.

## Sources

- A saved rbp word (0x7ff...) — saved_ret = *rbp_prev + 8.
- An argv/env pointer — points to the stack top.
- A pointer-to-stack arg (a local buffer's address passed to printf).

## Steps

1. Scan the %p dump for 0x7ff...-shaped words.
2. Each is a stack pointer — compute your target's slot from it.
3. The rbp-chain walk: rbp, *rbp = old rbp, *(old rbp)+8 = saved ret.
