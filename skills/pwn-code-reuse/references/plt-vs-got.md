# PLT vs GOT — which address does what


- PLT[x]: the call site — a stub that jumps through GOT[x]; calling it
  calls the resolved function.
- GOT[x]: the resolved pointer — reading it leaks the libc address;
  writing it (partial RELRO) redirects the call.

## The usage

- To CALL a function: ret to plt[x] — the call goes through.
- To LEAK a function's address: print the contents of got[x].
- To REDIRECT a call: write got[x] (needs partial RELRO + a write
  primitive).

## Falsifier

Confusing the two: calling got[x]'s contents directly isn't a gadget —
the PLT stub is the call entry.
