# x64 vs x86 — the arg convention — deep

Companion to `the-64-vs-32.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
