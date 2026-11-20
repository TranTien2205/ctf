# Trap: offset drift remote-vs-local

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

env/argv length shifts the stack layout; a pad that lands locally can be 8-64 bytes off remotely - measure against the service wrapper, pad with a cyclic tail, or use a pointer-into-buffer instead of stack offset.

## Pivot

Module read -> the shared file or class skill it names.
