# Identifying the libc — the fingerprint check — deep

Companion to `the-libc-id.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
