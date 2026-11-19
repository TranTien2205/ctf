# x64 vs x86 — the arg convention


- x64: args in rdi, rsi, rdx, rcx, r8, r9 — pop gadgets set them.
- x86: args on the stack — the chain embeds them after the call
  target: [func][ret-addr][arg0][arg1]...

## The x86 chain shape

    [func_addr] [the_return_addr_or_next_gadget] [arg0] [arg1] ...

Args are stack words, not popped registers — a different layout.

## Falsifier

Wrong ABI assumed: the chain's argument placement fails — check the
binary's class first.
