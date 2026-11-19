# The call after the write — what actually fires


Between your %n write and the redirect's firing, the program keeps
running: the next printf, the next malloc, the next return — whichever
reads the corrupted pointer first fires it.

## The lag

- GOT[x] written → fires on the NEXT call of that import.
- Ret-addr written → fires at function return.
- Hook written → fires at next malloc/free.
- A dead write (target never read again) never fires.

## Falsifier

The corrupted pointer is never dereferenced before exit: the write never
fires.
