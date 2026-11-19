# The write-target table — GOT vs ret-addr vs hook — case catalogue

Three redirectable targets for a %n write: a GOT entry (call-time redirect), a saved return address (return-time), a malloc/free hook (alloc-time). Choose by what's reachable and what fires.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | partial RELRO + an import called next | GOT | the call |
| 2 | a known stack ret-addr | return | the ret |
| 3 | glibc ≤2.34 + a free after | free_hook | the alloc |
| 4 | the target's call-arg is right | the redirect calls it | arg check |

## Falsifier

Falsifier — none of the three is writable/reachable/firable: no %n redirect exists.
