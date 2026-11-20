# Firmware analysis

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

firmware-analysis.md owns the deep rootfs audit - the
router's intake stops at extraction; the depth file
carries the audit.

## Pivot

Module read -> the depth file or sibling module the artifact names.
