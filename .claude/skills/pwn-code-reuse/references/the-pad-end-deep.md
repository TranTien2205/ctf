# Padding to the chain's end — the trailing bytes — deep

Companion to `the-pad-end.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
