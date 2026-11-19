# The esp-chain — x86 layout — deep

Companion to `the-esp-chain.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
