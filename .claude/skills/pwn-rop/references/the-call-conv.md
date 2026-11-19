# The calling conventions — SysV vs Win vs x86


- x64 SysV (Linux): rdi rsi rdx rcx r8 r9.
- x64 Windows: rcx rdx r8 r9 — different order!
- x86 cdecl: stack args.

## The check

The target's ABI — a Windows or x86 binary needs the different arg
map; the chain built for SysV fails silently.
