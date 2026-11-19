# ret2dlresolve — resolving a symbol that was never imported — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| no useful import but _dl_runtime_resolve exists | fake-resolve possible | ret2dlresolve |
| partial/no RELRO makes the link_map writable | the resolver takes your entries | the chain |
| a controllable relocation index | the fake entries reachable | lay them out |

## Falsifier

Falsifier — no writable place for the fake structures, or the resolver stub isn't reachable: ret2dlresolve can't run.
