# The 7th arg — the stack-supplied argument


Args 7+ go on the stack — placed after the call target:

    [pops for 1-6] [call] [ret_of_call] [arg7] [arg8]...

## The layout

The called function reads them at [rsp+8], [rsp+16]... — the chain
supplies them there.
