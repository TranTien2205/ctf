# The wrong order — common sequence bugs — checklist

Companion to `the-order-wrong.md`.

## Checklist

- [ ] Pop before the offset: the gadget lands in the buffer, not at rip.
- [ ] Arg before the pop: the pop consumes the wrong qword.
- [ ] Call before the args: the call sees unset registers.
- [ ] Ending before the work: the chain exits before the payload.
