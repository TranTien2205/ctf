# Args past rdi/rsi — the harder registers


Args 3+ (rdx, rcx, r8, r9) have scarcer pop gadgets — substitutes:

- rdx: `pop rdx` rare — `mov rdx, r15`-shaped or ret2csu.
- rcx/r8/r9: usually needed only for exotic calls — most chains stop
  at three args.

## The syscall-arg order

x64 syscall: rdi, rsi, rdx, r10 (NOT rcx), r8, r9 — r10 for arg4 is
especially rare; design to need <= 3 args.

## Falsifier

The needed call requires an arg register no gadget reaches: restructure
the call (a different function, a two-step).
