# Leaking through the GOT — puts(puts@got) — deep

Companion to `leak-the-got.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
