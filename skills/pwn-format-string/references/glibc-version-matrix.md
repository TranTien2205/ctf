# The glibc version matrix — which targets exist

| glibc | Hooks | GOT |
|---|---|---|
| ≤ 2.34 | __malloc_hook, __free_hook writable | RELRO-dependent |
| ≥ 2.35 | hooks removed | RELRO-dependent |

Check the version from the shipped libc or a leak — the hook targets only
exist on ≤2.34. Newer glibc → GOT or ret-addr only.
