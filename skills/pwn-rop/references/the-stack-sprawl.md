# The stack sprawl — when the chain is huge


A long chain sprawls across the buffer — the ending lands far past
the overwrite; the layout:

    [pad][g1][a1][g2][a2][ret][call][ending]

Each entry a qword; the walk is sequential; a mid-chain corrupt byte
breaks everything after it.
