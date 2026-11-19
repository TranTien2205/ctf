# The env pointer — a stack-window leak — deep

Companion to `the-env-ptr.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
