# The chain as data — writing the exploit file — deep

Companion to `the-chain-file.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
