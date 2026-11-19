# PLT vs GOT — which address does what — checklist

Companion to `plt-vs-got.md`.

## Checklist

- [ ] PLT[x]: the call site — a stub that jumps through GOT[x]; calling it
- [ ] GOT[x]: the resolved pointer — reading it leaks the libc address;
- [ ] To CALL a function: ret to plt[x] — the call goes through.
- [ ] To LEAK a function's address: print the contents of got[x].
- [ ] To REDIRECT a call: write got[x] (needs partial RELRO + a write
