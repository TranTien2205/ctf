# Ending the chain — the final landing


The chain ends on a target that produces observable output: a flag print,
a shell, an exit — the last redirect should terminate in evidence.

## Steps

1. The last write's target is where execution lands.
2. Prefer targets that produce output (flag-printing func, system).
3. A landing that produces no observable effect can't be confirmed.

## Falsifier

The redirect fires but nothing observable happens: the target was wrong
or the output went elsewhere.
