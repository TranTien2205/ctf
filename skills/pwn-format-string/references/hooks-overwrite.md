# __malloc_hook / __free_hook overwrite — old glibc

On glibc ≤ 2.34, __malloc_hook and __free_hook are writable function pointers called on every malloc/free — a %n write to them gives a hook that fires on the next allocation.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| glibc ≤ 2.34 | hooks exist | writable hook targets |
| a malloc/free happens after the write | the hook fires | redirect |
| __free_hook = system | free("/bin/sh") → shell | the classic |

## Steps

1. Check the glibc version — hooks were removed in 2.35.
2. Plant __free_hook's address as a %N$n arg; write system's address.
3. Arrange a free of a chunk containing '/bin/sh' → free calls system('/bin/sh').
4. Alternatively __malloc_hook fires on the next malloc.

## Falsifier

Falsifier — glibc ≥ 2.35: the hooks are gone; use GOT or ret-addr instead.

## Traps

- __free_hook = system + a freed chunk holding '/bin/sh' is the classic.
- The hooks are libc globals — need the libc base under ASLR.
- Removed in glibc 2.35 — check the version.

## Cross-references

`got-overwrite-fmt.md` · `glibc-version-matrix.md`
