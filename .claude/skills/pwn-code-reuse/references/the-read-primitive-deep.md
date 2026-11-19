# The read primitive — the mov-load gadget — deep

Companion to `the-read-primitive.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
