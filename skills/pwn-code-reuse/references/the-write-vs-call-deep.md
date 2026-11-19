# Write vs call — which ends the exploit — deep

Companion to `the-write-vs-call.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
