# Negative: no deciding check

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

A binary with no accept/reject surface - a crackme has
a check; a utility binary does not. If there is no
check, the challenge is elsewhere (hidden data,
stego, misc).

## Pivot

Module read -> the depth file or sibling module the artifact names.
