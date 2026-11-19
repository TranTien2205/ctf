# The destructor slot — __do_global_dtors — deep

Companion to `the-dtor-slot.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
