# The 32-bit chain shape — stack args — deep

Companion to `the-vs-32.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
