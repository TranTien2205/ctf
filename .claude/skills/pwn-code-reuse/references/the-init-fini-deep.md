# .init/.fini — the startup-ending arrays — deep

Companion to `the-init-fini.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
