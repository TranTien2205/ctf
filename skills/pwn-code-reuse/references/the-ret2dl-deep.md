# ret2dlresolve — the no-leak call — deep

Companion to `the-ret2dl.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
