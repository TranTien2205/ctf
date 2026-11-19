# The recheck loop — iterate the failing stage — deep

Companion to `the-recheck-loop.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
