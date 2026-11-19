# The vptr — the C++ object's first field — checklist

Companion to `the-vptr-field.md`.

## Checklist

- [ ] 1. Overlap a controllable object with a polymorphic one.
- [ ] 2. Write the vptr = your fake vtable's address.
- [ ] 3. The next virtual call dispatches through your table.
