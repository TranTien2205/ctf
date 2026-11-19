# The two-arg call — pop rdi + pop rsi


Two-arg calls (the common second stage):

    pop rdi ; arg0
    pop rsi ; arg1
    the_call

Or a combined `pop rsi; pop r15; ret` gadget for rsi (+ a scratch r15).

## Falsifier

No rsi-reaching gadget: a different call shape.
