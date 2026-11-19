# The jump table — the switch's gadget field


A switch statement's jump table is a field of `jmp [base + idx*8]`
targets — indexed dispatch; occasionally a usable pivot/call
primitive.
