# Restarting — ret to main for stage 2 — deep

Companion to `the-restart.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
