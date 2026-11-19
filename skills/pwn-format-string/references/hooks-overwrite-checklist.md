# __malloc_hook / __free_hook overwrite — old glibc — checklist

On glibc ≤ 2.34, __malloc_hook and __free_hook are writable function pointers called on every malloc/free — a %n write to them gives a hook that fires on the next allocation.

## Checklist

- [ ] Check the glibc version — hooks were removed in 2.35.
- [ ] Plant __free_hook's address as a %N$n arg; write system's address.
- [ ] Arrange a free of a chunk containing '/bin/sh' → free calls system('/bin/sh').
- [ ] Alternatively __malloc_hook fires on the next malloc.

## Abort conditions

- __free_hook = system + a freed chunk holding '/bin/sh' is the classic.
- The hooks are libc globals — need the libc base under ASLR.
- Removed in glibc 2.35 — check the version.

## Falsifier

Falsifier — glibc ≥ 2.35: the hooks are gone; use GOT or ret-addr instead.
