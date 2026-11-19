# The two-arg call — pop rdi + pop rsi — deep

Companion to `the-two-arg.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
