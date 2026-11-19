# ROP + heap — the write's landing — deep

Companion to `the-heap-combo.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
