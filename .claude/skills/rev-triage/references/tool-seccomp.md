# tools/seccomp_dump.py

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

BPF filter extraction from the binary - names allowed/
denied syscalls without running it; seccomp-tools absent.

## Pivot

Module read -> the depth file or sibling module the artifact names.
