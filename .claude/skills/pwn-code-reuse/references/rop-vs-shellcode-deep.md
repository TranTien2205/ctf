# ROP vs shellcode — when NX is off — deep

Companion to `rop-vs-shellcode.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
