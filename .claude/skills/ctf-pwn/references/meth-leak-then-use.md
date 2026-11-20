# Leak before reuse

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

PIE/ASLR binaries need an address primitive before any reuse chain: fmt leak, overwrite-partial, puts@plt round-trip, uninitialized read - name WHICH leak feeds the chain before writing it.

## Pivot

Module read -> the shared file or class skill it names.
