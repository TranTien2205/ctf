# tools/forensics/squashfs_read.py

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

squashfs without unsquashfs - list walks the dir table,
get extracts blocks+fragments (zlib; others report id).

## Pivot

Module read -> the depth file or sibling module the artifact names.
