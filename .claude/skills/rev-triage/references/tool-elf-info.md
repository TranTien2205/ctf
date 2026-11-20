# tools/elf_info.py

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

Sections, symbols, DT_NEEDED, relocations, GOT write
targets, check-naming imports (*cmp* *crypt* *verif*
*pass*) - the ELF intake without readelf/nm.

## Pivot

Module read -> the depth file or sibling module the artifact names.
