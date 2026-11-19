# Setting the args — the register-pop discipline


Args are set BEFORE the call — the pops must precede the call target:

    pop rdi ; arg0
    pop rsi ; arg1
    pop rdx ; arg2
    call_target

## The order

The pops' order doesn't matter (each sets an independent register) —
only that they all precede the call and no gadget clobbers an
already-set register.
