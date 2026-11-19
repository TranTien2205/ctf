# __malloc_hook / __free_hook overwrite — old glibc — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| glibc ≤ 2.34 | hooks exist | writable hook targets |
| a malloc/free happens after the write | the hook fires | redirect |
| __free_hook = system | free("/bin/sh") → shell | the classic |

## Falsifier

Falsifier — glibc ≥ 2.35: the hooks are gone; use GOT or ret-addr instead.
