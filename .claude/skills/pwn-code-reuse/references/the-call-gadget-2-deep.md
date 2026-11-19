# call reg — the indirect call gadget — deep

Companion to `the-call-gadget-2.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
