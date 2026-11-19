# The call after the write — what actually fires — checklist

Companion to `the-call-after-write.md`.

## Checklist

- [ ] GOT[x] written → fires on the NEXT call of that import.
- [ ] Ret-addr written → fires at function return.
- [ ] Hook written → fires at next malloc/free.
- [ ] A dead write (target never read again) never fires.
