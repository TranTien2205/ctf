# TLS destructors — the thread-local hook — deep

Companion to `the-tls-dtor.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
