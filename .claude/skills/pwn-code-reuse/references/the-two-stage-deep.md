# The two-stage chain — leak then execute — deep

Companion to `the-two-stage.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
