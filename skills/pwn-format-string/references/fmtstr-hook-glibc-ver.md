# __free_hook/__malloc_hook — the glibc version bound


The hook targets exist only on glibc <= 2.34 (removed in 2.35+). On
newer glibc the slots are gone — check the version first.

## Steps

1. Leak libc — identify the version (strings on the .so, or
   gnu_get_libc_version via a leak).
2. glibc <= 2.34: __free_hook/__malloc_hook writable, %n writes work.
3. glibc >= 2.35: hooks removed — ret-addr or other slots instead.

## The write

- __free_hook = system → next free(ptr) calls system(ptr) — free a
  buffer holding "/bin/sh".
- __malloc_hook = one_gadget-ish → next malloc fires it (needs a gadget).

## Falsifier

glibc > 2.34 or the hooks are nulled: the slots don't exist.
