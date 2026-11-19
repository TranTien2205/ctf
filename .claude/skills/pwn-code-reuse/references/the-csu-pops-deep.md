# The csu pops — the universal register setter — deep

Companion to `the-csu-pops.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
