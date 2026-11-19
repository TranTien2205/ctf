# .init_array — the startup list


The array of constructors run before main — a writable target on
partial RELRO: overwrite an entry, the function runs at the next
startup (rarely re-reachable mid-run).

## The more useful .fini_array

Runs at exit — the exit-path redirect.
