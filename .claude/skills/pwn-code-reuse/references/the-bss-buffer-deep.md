# The .bss buffer — a fixed plant region — deep

Companion to `the-bss-buffer.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
