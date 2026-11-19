# Verifying the call — did it fire — deep

Companion to `the-call-verify.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
