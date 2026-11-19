# Use-after-free — the canonical heap bug


A pointer survives free(): the object is freed, the dangling reference
still reads/writes it — and the allocator may hand it back as a
different object.

## The primitive ladder

1. dangling read → reads chunk metadata or a reallocated object's data.
2. dangling write → writes into a chunk now owned by a different
   object — type confusion.
3. double-alloc overlap → two live objects share memory.

## Steps

1. Free the object; keep the pointer.
2. Reallocate a different type into the same slot (same-size alloc).
3. Read/write via the dangling pointer — it now aliases the new object.

## Signals

- freed object fields still readable: metadata bytes (fd/key) leak.
- writing the dangled object changes a different object's fields.

## Falsifier

The free nulls the pointer (or every path re-checks): no dangling access
exists — the UAF is closed.
