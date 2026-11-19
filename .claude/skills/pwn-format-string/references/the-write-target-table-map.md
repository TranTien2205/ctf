# The write-target table — GOT vs ret-addr vs hook — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| partial RELRO + an import called next | GOT | the call |
| a known stack ret-addr | return | the ret |
| glibc ≤2.34 + a free after | free_hook | the alloc |
| the target's call-arg is right | the redirect calls it | arg check |

## Falsifier

Falsifier — none of the three is writable/reachable/firable: no %n redirect exists.
