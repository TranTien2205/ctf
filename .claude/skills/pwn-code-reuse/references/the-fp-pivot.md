# The saved-fp pivot — leave;ret explained


`leave; ret` = mov rsp,rbp ; pop rbp ; ret — if you control rbp, the
next ret pops your chain's first address from where rbp points.

## The recipe

1. Overflow sets rbp = your-chain-buffer (in a second write or a
   leaked-known region).
2. The function's epilogue `leave; ret` pivots rsp into your buffer.
3. The chain runs from there.

## Falsifier

rbp isn't controllable or the buffer's address isn't known: the pivot
can't aim.
