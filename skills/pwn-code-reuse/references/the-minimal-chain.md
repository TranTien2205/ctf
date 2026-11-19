# The minimal chain — 3 entries


The shortest real exploit (non-PIE + win function):

    <padding>
    [pop rdi ; ret]     # if the win func needs an arg
    [arg]
    [win_addr]

Or even shorter: [win_addr] alone if it needs no args and alignment
is already right.
