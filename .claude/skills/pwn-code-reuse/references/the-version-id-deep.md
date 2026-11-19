# Identifying the libc version — the fingerprint — deep

Companion to `the-version-id.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
