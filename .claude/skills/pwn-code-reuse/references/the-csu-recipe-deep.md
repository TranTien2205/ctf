# The ret2csu recipe — the full sequence — deep

Companion to `the-csu-recipe.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
