# __malloc_hook / __free_hook overwrite — old glibc — case catalogue

On glibc ≤ 2.34, __malloc_hook and __free_hook are writable function pointers called on every malloc/free — a %n write to them gives a hook that fires on the next allocation.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | glibc ≤ 2.34 | hooks exist | writable hook targets |
| 2 | a malloc/free happens after the write | the hook fires | redirect |
| 3 | __free_hook = system | free("/bin/sh") → shell | the classic |

## Falsifier

Falsifier — glibc ≥ 2.35: the hooks are gone; use GOT or ret-addr instead.
