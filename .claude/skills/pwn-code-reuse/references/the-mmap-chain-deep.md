# mmap — allocating a page — deep

Companion to `the-mmap-chain.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
