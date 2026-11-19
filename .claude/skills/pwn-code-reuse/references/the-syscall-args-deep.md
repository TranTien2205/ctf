# Syscall arg mapping — the kernel's order — deep

Companion to `the-syscall-args.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
