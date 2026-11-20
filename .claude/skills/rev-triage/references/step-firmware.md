# Firmware intake

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

binwalk -e extracts, squashfs_read.py lists/extracts the
rootfs without unsquashfs, dtb_dump.py reads the device tree.
The rootfs is the analysis surface.

## Pivot

Module read -> the depth file or sibling module the artifact names.
