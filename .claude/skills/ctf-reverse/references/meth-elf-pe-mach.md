# ELF vs PE vs Mach-O reading

Depth module for `ctf-reverse`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Format decides the tool and the traps: ELF sections/symbols via
readelf (`-h -S -s -d -l`); PE imports/sections via objdump or
strings-based recon when radare2; Mach-O via otool-class flags or
r2. `pwn_triage.py` covers the ELF protections path on this box;
the absent-tool list (gdb, ROPgadget, pwntools) means radare2 is
the dynamic story for every format.

## Pivot

Format identified -> the matching patterns file and class skill.
