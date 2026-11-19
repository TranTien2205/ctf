# RELRO and the GOT — the write question — deep

Companion to `partial-vs-full-relro.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
