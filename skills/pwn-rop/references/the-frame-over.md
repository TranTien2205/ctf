# Frame overlap — the callee's locals


The callee's locals occupy stack space above the chain — they don't
corrupt it (the chain's entries are below); the walk continues when
the callee returns.
