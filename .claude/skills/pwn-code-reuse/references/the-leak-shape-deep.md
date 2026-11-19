# The leak's shape — the bytes that come back — deep

Companion to `the-leak-shape.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
