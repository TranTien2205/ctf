# Verifying the call target — before the chain — deep

Companion to `the-call-target-check.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
