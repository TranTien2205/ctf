# Syscall numbers — the rax values — deep

Companion to `the-syscall-num.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
