# ret2dlresolve — resolving a symbol that was never imported — case catalogue

The dynamic linker's lazy-resolution machinery can be tricked into resolving an ARBITRARY symbol name at runtime: craft fake relocation/symbol/string entries, call the resolver stub, and 'system' materializes even though the binary never imported it.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | no useful import but _dl_runtime_resolve exists | fake-resolve possible | ret2dlresolve |
| 2 | partial/no RELRO makes the link_map writable | the resolver takes your entries | the chain |
| 3 | a controllable relocation index | the fake entries reachable | lay them out |

## Falsifier

Falsifier — no writable place for the fake structures, or the resolver stub isn't reachable: ret2dlresolve can't run.
