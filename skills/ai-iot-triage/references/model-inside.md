# What's inside a checkpoint

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

A .pt/.pkl is pickled tensors plus code - the
deserialization view treats it as a program; the flag may
be a tensor, a code object, or a separate member of the
archive.

## Pivot

Module read -> the router or sibling module the observation names.
