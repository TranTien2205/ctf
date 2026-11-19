# The Elf64_Rela — the relocation's shape — deep

Companion to `the-rela-entry.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
