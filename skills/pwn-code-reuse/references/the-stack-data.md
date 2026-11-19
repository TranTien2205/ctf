# Stack-resident data — the args on the stack


Args beyond the registers (or x86's args entirely) are stack entries —
the chain's stack-args region sits after the call target, read as the
call's incoming arguments.
