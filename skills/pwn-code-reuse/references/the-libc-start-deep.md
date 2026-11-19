# __libc_start_main — the main caller — deep

Companion to `the-libc-start.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
