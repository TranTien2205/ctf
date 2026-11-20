# WASM module

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

\0asm magic - wasm2wat/wabt decompiles; the linear memory
and the export table are the audit surface.

## Pivot

Module read -> the depth file or sibling module the artifact names.
