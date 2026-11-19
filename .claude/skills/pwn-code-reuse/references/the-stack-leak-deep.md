# The stack leak — for ret-addr targets — deep

Companion to `the-stack-leak.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
