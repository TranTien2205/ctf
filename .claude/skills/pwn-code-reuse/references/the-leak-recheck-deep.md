# Re-checking the leak — the version confirm — deep

Companion to `the-leak-recheck.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
