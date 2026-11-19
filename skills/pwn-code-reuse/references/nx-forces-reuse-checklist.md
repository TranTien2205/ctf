# NX forces reuse — why the payload is borrowed — checklist

Companion to `nx-forces-reuse.md`.

## Checklist

- [ ] Every action is a gadget: pop a register, a syscall, a call.
- [ ] The chain is a stack of gadget addresses + arguments.
- [ ] Missing gadgets constrain what the chain can express.
