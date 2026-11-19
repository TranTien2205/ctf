# Where the args actually sit — the stack picture


On x64, printf(rdi=fmt, rsi..r9, stack-args): the varargs START at rsi;
the 'Nth arg' for %N$p counts from rsi=1. Stack-resident args begin where
registers run out.

## The layout

- printf's FIRST arg is rdi (the format) — specifiers count varargs:
  rsi=1.
- %1$p=rsi ... %6$p=r9; %7$p+ = stack.
- Your input buffer lives on the stack → typically N≥7.

## Falsifier

Windows x64 ABI differs (rcx,rdx,r8,r9 + shadow space — 4 register args):
the window starts at N=5 there.
