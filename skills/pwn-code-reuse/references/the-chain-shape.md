# The chain's shape — addresses and arguments


A ROP chain is a sequence: gadget address, its argument (if a pop),
next gadget address, its argument — laid out in the overflow buffer
past the saved-return slot.

## The layout (x64, ret-chain)

    <padding to ret slot>
    [pop_rdi_gadget] [arg0]
    [pop_rsi_gadget] [arg1]
    [pop_rdx_gadget] [arg2]
    [call_target]
    ...

## The rule

Each `pop rXX; ret` consumes TWO qwords (the gadget's address, then the
popped value); a bare `ret` consumes one; a `call`/`jmp` consumes one
and transfers control.
