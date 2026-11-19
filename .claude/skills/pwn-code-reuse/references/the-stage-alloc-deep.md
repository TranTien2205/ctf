# The staged alloc — read into memory — deep

Companion to `the-stage-alloc.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
