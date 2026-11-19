# Gadget side effects — the hidden costs


A gadget's full tail may do more than its headline:

- extra pops (consumes extra qwords — the chain must provide them).
- memory writes (clobbers a region).
- conditional jumps (control may not reach the ret).

## The rule

Audit each gadget; a side-effectful gadget changes the stack budget
and the state.
