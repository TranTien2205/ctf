# The scratch slots — r15 and friends — deep

Companion to `the-empty-slots.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
