# Tcache poisoning — aiming the fd pointer


Overwrite a tcache chunk's `e->next` (fd) so the next malloc returns
attacker-chosen memory — the shortest write primitive on the heap.

## Steps (glibc <= 2.31, no safe-linking)

1. Free a chunk → it lands in tcache with a real fd.
2. UAF-write or overflow: set fd = target_address.
3. Two mallocs of that size: first returns the freed chunk, second
   returns target_address.
4. Write into the "allocated" chunk → arbitrary write.

## glibc >= 2.32 (safe-linking)

fd is stored mangled: `PROTECT_PTR(pos, ptr) = (pos>>12) ^ ptr`. To aim
it you must know a heap address — the leak precedes the poison:

    mangled = (chunk_addr >> 12) ^ target

## Falsifier

No way to write the fd and no leak to de-mangle (2.32+): the poison
can't aim — a different primitive is needed.
