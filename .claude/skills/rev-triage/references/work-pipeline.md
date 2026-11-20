# The pipeline

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

identify -> decompile -> find the deciding check -> replicate it.
Four steps; the order is load-bearing because each step's output
bounds the next one's cost.

## Pivot

Module read -> the depth file or sibling module the artifact names.
