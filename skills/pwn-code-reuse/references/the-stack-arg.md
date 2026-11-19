# The stack-arg call — x86 convention


x86: the call's args are stack entries after the call target — the
chain embeds them: [func][ret][arg0][arg1].

## The shape

To call system("/bin/sh"): [system][exit][binsh] — system's return
goes to exit; its arg is binsh.
