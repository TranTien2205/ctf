# Write-then-trigger — the timing of the redirect


The %n write and the redirect's firing are separate events: the write
happens during printf; the redirect fires when the affected pointer is
next dereferenced.

## The lag

- GOT write → fires on the NEXT call of that import.
- Ret-addr write → fires at function return.
- Hook write → fires at the next malloc/free.
- A dead write (target never read again) never fires.

## Steps

1. Write the redirect.
2. Trigger the firing event (cause the call/return/alloc).
3. The behavior change IS the confirmation.
