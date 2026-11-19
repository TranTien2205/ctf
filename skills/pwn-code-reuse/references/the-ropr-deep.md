# The ROP reporter — what pwn_triage gives — deep

Companion to `the-ropr.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
