# Ordering the ops — the write then call — deep

Companion to `the-ordering.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
