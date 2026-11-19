# The link_map — the resolver's context — deep

Companion to `the-linkmap.md`.

Code reuse borrows the binary's own instruction tails — ret-terminated gadgets + register arguments, laid out on the stack. NX forces it; gadget availability constrains it.
