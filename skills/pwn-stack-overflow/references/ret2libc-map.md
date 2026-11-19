# ret2libc — call libc functions via a leak — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| libc linked, ASLR on | need a libc leak | leak via puts/printf/read |
| a GOT entry you can print | base recoverable | puts(GOT[x]) |
| no useful import but libc present | libc functions reachable | compute + call |

## Falsifier

Falsifier — no leak primitive exists (no read to an address you control, no puts of a pointer): libc base stays hidden; ret2libc is out without it.
