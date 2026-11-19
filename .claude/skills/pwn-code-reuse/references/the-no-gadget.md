# When there's no gadget — the last resorts


A tiny binary with almost no gadgets: the last resorts are —

- ret2csu (the __libc_csu_init sequence).
- A call through an existing function pointer (GOT/app slots).
- SROP (one syscall gadget suffices).
- A jump into the middle of a function with the right stack shape.

## Falsifier

Even those are absent: the write must target data, not code — the
redirect goes through a pointer, not a chain.
