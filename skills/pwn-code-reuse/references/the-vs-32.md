# The 32-bit chain shape — stack args


x86: the call's arguments are stack entries — after the call target,
the stack is: the return address, then arg0, arg1...

## The layout

    [func][ret_or_gadget][arg0][arg1][arg2]

To call system("/bin/sh"): [system][exit][binsh_addr] — the "return
address" slot becomes the next call's entry.
