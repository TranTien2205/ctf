# libc gadgets — when the binary is thin — deep

Companion to `the-libc-gadgets.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
