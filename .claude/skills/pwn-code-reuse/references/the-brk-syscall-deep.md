# brk — the simpler alloc syscall — deep

Companion to `the-brk-syscall.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
