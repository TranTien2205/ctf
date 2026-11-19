# Detecting heap corruption — the first signals


The class announces itself through behavior, not a signature: crashes
inside malloc/free, allocator aborts, weird allocation results.

## Signals

- A crash inside `_int_malloc`, `_int_free`, tcache_put/get — the
  corruption happened earlier, the crash is downstream.
- glibc abort messages: "double free or corruption", "corrupted top
  size", "free(): invalid pointer", "malloc(): memory corruption".
- A realloc'd object whose fields alias another object's — an overlap.
- An alloc that returns the same address twice while both are "live".

## The first confirmation

Free an object, keep using its pointer: if the freed object's fields
change (or a new alloc lands there while the pointer works), a
dangling reference exists — the class is open.

## Falsifier

Every freed object becomes unreachable (pointer cleared, accesses
bounds-checked): no dangling access — the class is closed.
