# ret2libc — call libc functions via a leak — case catalogue

When the binary imports no system but links libc, a leak of ANY libc address plus the known offset reaches system()/execve(). The chain is leak → compute base → call.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | libc linked, ASLR on | need a libc leak | leak via puts/printf/read |
| 2 | a GOT entry you can print | base recoverable | puts(GOT[x]) |
| 3 | no useful import but libc present | libc functions reachable | compute + call |

## Falsifier

Falsifier — no leak primitive exists (no read to an address you control, no puts of a pointer): libc base stays hidden; ret2libc is out without it.
