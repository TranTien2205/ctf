# When there's no gadget — the last resorts — checklist

Companion to `the-no-gadget.md`.

## Checklist

- [ ] ret2csu (the __libc_csu_init sequence).
- [ ] A call through an existing function pointer (GOT/app slots).
- [ ] SROP (one syscall gadget suffices).
- [ ] A jump into the middle of a function with the right stack shape.
