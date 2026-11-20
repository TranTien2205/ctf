# Embedded binary

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

An ARM/MIPS binary runs under qemu-<arch>-static (chrooted
when needed) - then it is a pwn or rev challenge in a
different ISA. `../../pwn-binary-triage/` owns it once it
executes.

## Pivot

Module read -> the router or skill the boundary names, or the sibling
module the artifact points to.
