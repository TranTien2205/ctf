# The second stage — read() into a bigger buffer — deep

Companion to `the-second-stage.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
