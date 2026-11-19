# PLT stub resolution — how ret2plt works


ret2plt's decode: .rela.plt names the symbol's GOT slot; the .plt's
`ff 25` stubs jmp through those slots — the stub referencing your
symbol's slot is the call address.

## The consequence

call plt[x] reaches the resolved function — the stub is the fixed
binary address; the resolved pointer is in the GOT.
