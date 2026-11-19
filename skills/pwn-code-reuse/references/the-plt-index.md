# The PLT index — where the stubs live


Each PLT entry is a fixed-size stub at .plt + i*0x10 — the import's
call address is the STUB, not the resolved function.

## The note

call plt[x] = call the resolved function (through the stub).
The resolved ADDRESS is in got[x] — a different thing.
