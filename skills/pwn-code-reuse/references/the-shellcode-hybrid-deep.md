# The shellcode hybrid — chain to code — deep

Companion to `the-shellcode-hybrid.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
