# Replicate, don't reverse

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

The solve is reproducing the check's logic (reimplement the
transform, invert the constraint) - full decompilation is a
means, not the deliverable.

## Pivot

Module read -> the depth file or sibling module the artifact names.
