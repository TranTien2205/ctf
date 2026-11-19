# The static binary — no libc to ret to — deep

Companion to `the-static-binary.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
