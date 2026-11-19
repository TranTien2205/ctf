# syscall/int 0x80 — the direct path — deep

Companion to `syscall-gadgets.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
