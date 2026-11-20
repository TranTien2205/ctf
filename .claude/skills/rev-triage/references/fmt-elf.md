# ELF recognition

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

\x7fELF magic - readelf -h for type (EXEC vs DYN=PIE) and
machine; the imports list names the bug families present.

## Pivot

Module read -> the depth file or sibling module the artifact names.
