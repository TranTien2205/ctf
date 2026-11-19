# The chain's length — the qword count


Count the qwords: each gadget + each arg is one — the total is the
payload's length past the offset; against the read's bound.

## The measure

    len(pops) + len(args) + len(the call) + len(the ending)
