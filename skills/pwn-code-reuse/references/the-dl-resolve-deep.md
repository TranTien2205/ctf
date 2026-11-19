# _dl_runtime_resolve — the resolver itself — deep

Companion to `the-dl-resolve.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
