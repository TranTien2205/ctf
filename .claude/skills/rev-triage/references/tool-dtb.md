# tools/forensics/dtb_dump.py

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

FDT blob to node/property tree - vendor props and
chosen/bootargs are where handouts hide things.

## Pivot

Module read -> the depth file or sibling module the artifact names.
