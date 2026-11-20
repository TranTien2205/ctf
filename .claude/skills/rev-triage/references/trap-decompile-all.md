# Trap: decompiling everything

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

Reading the whole binary before finding the check - the
deciding check is usually one function; find it first
by the imports/strings/cmp hunt.

## Pivot

Module read -> the depth file or sibling module the artifact names.
