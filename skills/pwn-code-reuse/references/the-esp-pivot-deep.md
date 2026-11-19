# The esp/rsp pivot — moving the stack — deep

Companion to `the-esp-pivot.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
