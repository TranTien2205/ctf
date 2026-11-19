# Heap boundaries — where the class ends — checklist

Companion to `heap-the-boundaries.md`.

## Checklist

- [ ] If the bug is a data-only write: not heap corruption (it's a write
- [ ] If the overflow reaches only the stack region: pwn-stack-overflow.
- [ ] If the "corruption" is a logic bug (slot reuse, index confusion):
- [ ] If nothing allocator-state is reachable: the class is closed.
