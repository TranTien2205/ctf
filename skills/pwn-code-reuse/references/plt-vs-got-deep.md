# PLT vs GOT — which address does what — deep

Companion to `plt-vs-got.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
