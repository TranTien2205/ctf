# fgets — the bounded stage-2 read — deep

Companion to `the-fgets-path.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
