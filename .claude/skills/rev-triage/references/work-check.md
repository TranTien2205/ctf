# The deciding check

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

The code that answers accept/reject - a cmp chain, a license
verify, a flag check. Everything before it is context; the
replication targets the check, not the whole binary.

## Pivot

Module read -> the depth file or sibling module the artifact names.
