# Core dumps

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

ET_CORE is a process snapshot - elf_info.py reads PT_NOTE:
registers, argv, and the file map of where the flag lived
in the dead process.

## Pivot

Module read -> the depth file or sibling module the artifact names.
