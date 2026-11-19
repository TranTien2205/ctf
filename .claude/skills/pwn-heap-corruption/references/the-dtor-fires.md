# Destructors — the C++ free-path extras


C++ objects run ~dtor before free — the destructor is itself a call
window (vfunc/vtable) between the corruption and the free.

## Exploitation

- A vtable-corrupted object's delete fires your vfunc, THEN frees —
  two primitives in one op.
- Order: dtor first, free second — the call happens while the chunk is
  still allocated.

## Falsifier

No vtable on the object or delete isn't exposed: the call window is
absent.
