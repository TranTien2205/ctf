# Finding the offset — the cyclic way — deep

Companion to `the-offset-find.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
