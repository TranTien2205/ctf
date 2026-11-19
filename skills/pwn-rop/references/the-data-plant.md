# The .data plant — initialized writable


.data (vs .bss) is initialized writable — either works for planting;
the difference: .data's contents matter to the program (a pointer it
uses), .bss starts zero.
