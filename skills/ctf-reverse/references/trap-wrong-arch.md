# Trap: wrong arch assumptions

Depth module for `ctf-reverse`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

ARM shellcode in an x86 challenge, 32-bit assumptions on a 64-bit binary, thumb mode - `file`+readelf headers first; capstone disassembly needs the right arch flag.

## Pivot

Module read -> the shared file or class skill it names.
