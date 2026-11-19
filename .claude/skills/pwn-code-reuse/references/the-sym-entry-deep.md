# The Elf64_Sym — the symbol's shape — deep

Companion to `the-sym-entry.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
