# The complete picture — the layout diagram


    low addr
    [user input buffer ..........]
    [pad pad pad pad pad pad pad ]
    [saved rbp]                   ← maybe the pivot lever
    [gadget 1]                    ← saved rip
    [arg 1]
    [gadget 2]
    [arg 2]
    [ret]                         ← alignment
    [call target]
    [ending]
    high addr
