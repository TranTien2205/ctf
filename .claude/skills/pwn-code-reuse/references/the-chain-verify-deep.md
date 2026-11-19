# Verifying the chain — the r2 -d walk — deep

Companion to `the-chain-verify.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
