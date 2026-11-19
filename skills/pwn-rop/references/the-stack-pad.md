# The stack pad — between chain and red zone


If the chain lives where a callee's red zone reaches: pad — move the
chain's continuation above the reach, or accept the clobber if the
entries are already consumed.
