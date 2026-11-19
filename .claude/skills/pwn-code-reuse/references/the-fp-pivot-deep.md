# The saved-fp pivot — leave;ret explained — deep

Companion to `the-fp-pivot.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
