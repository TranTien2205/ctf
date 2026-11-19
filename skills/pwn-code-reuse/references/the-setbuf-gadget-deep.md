# The setbuf trick — planting a controlled frame — deep

Companion to `the-setbuf-gadget.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
