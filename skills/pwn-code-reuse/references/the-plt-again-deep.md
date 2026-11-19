# The PLT is enough — no-libc chains — deep

Companion to `the-plt-again.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
