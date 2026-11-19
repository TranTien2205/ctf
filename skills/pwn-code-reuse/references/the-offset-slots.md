# The slots — where each chain entry goes


    buf_end        = saved_rbp
    saved_rbp + 8  = saved_rip  ← the first chain slot
    saved_rip + 8  = gadget1's arg or gadget2
    ...

The chain's first entry IS the new rip — the rest follow.
