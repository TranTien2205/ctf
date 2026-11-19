# Multi-arg calls — stacking the args


Calls needing args past the registers (x64 arg 7+) go on the stack —
the stack-arg portion sits after the call target.

## The layout (x64, 8 args)

    [pops for rdi..r9] [call_target] [ret][arg7][arg8]

The stack args sit where the called function reads them.
