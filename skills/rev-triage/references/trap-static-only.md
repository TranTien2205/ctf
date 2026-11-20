# Trap: static-only analysis

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

A check that only reveals itself at runtime (computed
constants, timing) - r2 -d exists; a dynamic look costs
minutes against hours of static guessing.

## Pivot

Module read -> the depth file or sibling module the artifact names.
