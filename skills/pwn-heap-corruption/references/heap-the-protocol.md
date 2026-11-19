# The protocol — talking to the service


The ops are lines on a socket/menu — the protocol is:

    add <size>
<data>
    del <i>
    show <i>
    edit <i>
<data>

Script the sequence — a python driver with send/recv per op. Verify
each op's output before the next; a failed op mid-sequence shifts
every later assumption.
