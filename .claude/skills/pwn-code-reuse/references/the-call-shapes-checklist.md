# The call shapes — ret vs call vs jmp — checklist

Companion to `the-call-shapes.md`.

## Checklist

- [ ] Land on a function's address via ret: the stack is its frame.
- [ ] A `call func` gadget: explicit transfer.
- [ ] A `jmp reg` gadget: the register must hold the next target.
