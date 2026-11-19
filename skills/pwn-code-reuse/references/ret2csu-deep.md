# ret2csu — the universal call primitive — deep

Companion to `ret2csu.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
