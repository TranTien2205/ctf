# Splitting the chain — staged payloads — deep

Companion to `the-chain-in-parts.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
