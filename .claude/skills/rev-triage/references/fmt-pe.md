# PE recognition

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

MZ + PE header - a PE with a CLR header is managed-code
(dnSpy/ILSpy territory); native PE is the same rev pipeline
with different tools.

## Pivot

Module read -> the depth file or sibling module the artifact names.
