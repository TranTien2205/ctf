# radare2 is the dynamic story

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

gdb is absent: r2 -d ./chal debugs, r2 -A analyses, pdf @ main
disassembles, dcu runs-to, db sets breakpoints. Every dynamic
technique below runs under r2.

## Pivot

Module read -> the depth file or sibling module the artifact names.
