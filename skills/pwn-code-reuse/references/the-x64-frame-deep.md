# The x64 frame — the standard layout — deep

Companion to `the-x64-frame.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
