# Minimal gadget sets — the survival chain — checklist

Companion to `gadget-minimal.md`.

## Checklist

- [ ] A single `pop rdi; ret` + a win function = enough.
- [ ] No pop gadgets at all: ret2csu, or a jmp/call gadget that uses
- [ ] Only `syscall`: needs the regs settable some other way (prior
