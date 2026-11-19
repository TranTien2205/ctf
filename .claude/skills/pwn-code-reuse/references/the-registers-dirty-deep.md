# Register state at the overwrite — the free args — deep

Companion to `the-registers-dirty.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
