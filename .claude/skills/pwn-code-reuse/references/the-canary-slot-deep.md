# Placing the canary — the leak's slot — deep

Companion to `the-canary-slot.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
