# atoi/strtol — the int conversion gadget — deep

Companion to `the-atoi-gadget.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
