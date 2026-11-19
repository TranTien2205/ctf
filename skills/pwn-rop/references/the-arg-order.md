# Argument order — the pops' sequence


Args are set before the call — the pops precede the target; their
internal order is free EXCEPT a gadget's side effects can clobber an
already-set register.

## The x64 map

    rdi ← arg0 (the path/handle)
    rsi ← arg1
    rdx ← arg2
    rcx ← arg3 (function calls)
    r8/r9 ← args 4/5

## The syscall map (different!)

    rdi, rsi, rdx, r10, r8, r9 — r10 not rcx for arg4.
