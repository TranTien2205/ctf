# The pop gadgets — setting the argument registers


The argument registers are set by pop gadgets: `pop rdi; ret` for arg0,
`pop rsi; ret` arg1, `pop rdx; ret` arg2, `pop rcx`/`pop r8`/`pop r9`
for more — each needs its own gadget.

## The priority order

1. `pop rdi; ret` — the most common, needed first.
2. `pop rsi; ret` / `pop rdx; ret` — args 2 and 3.
3. `pop rax; ret` — the syscall number holder.
4. Combined: `pop rsi; pop r15; ret` — sets two (r15 is a scratch you
   can ignore).

## Missing gadgets

No `pop rdx`? The syscall route's arg2 can't be set directly — use a
`mov`/`xor`-shaped gadget or a different call convention (see
syscall-arg-workarounds).

## Falsifier

Not even `pop rdi` exists and no substitute sequence reaches the
argument registers: the chain can't set arguments — ret2csu or a
different call mechanism is needed.
