# x86 args — the stack-arg layout


x86: [func][ret][arg0][arg1]... — the args are stack qwords after the
call target, not pop-set registers.

## The call convention

The called function reads its args from [esp+4], [esp+8]... — the
chain's layout supplies them there.
