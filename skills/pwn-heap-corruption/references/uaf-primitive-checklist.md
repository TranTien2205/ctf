# Use-after-free — the canonical heap bug — checklist

Companion to `uaf-primitive.md`.

## Checklist

- [ ] 1. dangling read → reads chunk metadata or a reallocated object's data.
- [ ] 2. dangling write → writes into a chunk now owned by a different
- [ ] 3. double-alloc overlap → two live objects share memory.
- [ ] 1. Free the object; keep the pointer.
- [ ] 2. Reallocate a different type into the same slot (same-size alloc).
- [ ] 3. Read/write via the dangling pointer — it now aliases the new object.
- [ ] freed object fields still readable: metadata bytes (fd/key) leak.
- [ ] writing the dangled object changes a different object's fields.
