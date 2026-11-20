# tools/file_type.py

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

Stdlib identify: magic -> format + route (ELF->pwn_triage,
PE-CLR->managed-code, pyc/class/dex->bytecode-vm,
squashfs->firmware), windowed entropy, flag-format grep.
The tool for when file/strings/binwalk are absent.

## Pivot

Module read -> the depth file or sibling module the artifact names.
