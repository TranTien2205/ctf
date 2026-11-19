# The alignment fix — where the ret goes — deep

Companion to `the-align-fix.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
