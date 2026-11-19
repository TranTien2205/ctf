# PIE and the gadget addresses — base-relative — deep

Companion to `pie-and-rop.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
