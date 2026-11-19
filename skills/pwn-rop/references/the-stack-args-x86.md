# Stack args — the x86 call layout


x86 has no register args — the chain is [func][ret][arg0][arg1]:

    [system][exit][binsh]

system reads its arg at [esp+4] — the chain supplies it there.

## The exit slot

The second entry is the function's return address — put exit there
for a clean finish.
