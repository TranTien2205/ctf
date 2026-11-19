# mprotect — making a page executable — deep

Companion to `mprotect-chain.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
