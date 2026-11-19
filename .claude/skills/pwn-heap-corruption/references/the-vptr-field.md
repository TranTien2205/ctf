# The vptr — the C++ object's first field


A polymorphic object's first qword is the vptr — overlapping it with
attacker bytes makes every virtual call aim at your table.

## Steps

1. Overlap a controllable object with a polymorphic one.
2. Write the vptr = your fake vtable's address.
3. The next virtual call dispatches through your table.

## Falsifier

The object isn't polymorphic or the overlap doesn't cover offset 0:
no vptr to forge.
