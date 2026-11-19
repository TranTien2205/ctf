# The atexit list — the exit hook chain — deep

Companion to `the-atexit-list.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
