# The PLT stub — the call's entry shape


A PLT stub is `jmp [got[x]]` — calling it jumps through the resolved
pointer; the stub itself is a fixed binary address (PIE-relative).

## The use

call/ret to the PLT stub = calling the function — the import's entry.
