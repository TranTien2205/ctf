# The sigreturn frame — all registers at once — deep

Companion to `the-sig-frame.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
