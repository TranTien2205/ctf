# The double pivot — two moves


Sometimes one pivot can't reach the region: pivot to an intermediate,
then to the final region — the two-move.

## The shape

    leave; ret        # rsp = rbp (the intermediate)
    pop rsp ; target  # rsp = the real chain region
