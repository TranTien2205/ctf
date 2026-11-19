# Heap boundaries — where the class ends


- If the bug is a data-only write: not heap corruption (it's a write
  primitive — see the app's own corruption surface).
- If the overflow reaches only the stack region: pwn-stack-overflow.
- If the "corruption" is a logic bug (slot reuse, index confusion):
  the class is what the INDEX bug gives, not the allocator.
- If nothing allocator-state is reachable: the class is closed.

The boundary test names the real primitive.
