# The write-target table — GOT vs ret-addr vs hook — checklist

Three redirectable targets for a %n write: a GOT entry (call-time redirect), a saved return address (return-time), a malloc/free hook (alloc-time). Choose by what's reachable and what fires.

## Checklist

- [ ] GOT: partial RELRO, the import called next with the right arg.
- [ ] Ret-addr: the stack address must be leaked/known; fires on return.
- [ ] Hook: glibc ≤2.34; fires on the next malloc/free with the hooked arg.
- [ ] Choose by which fires with a useful argument state.

## Abort conditions

- GOT is the usual target (partial RELRO); hook for old glibc; ret-addr when stack addr is known.
- The redirect's arg comes from the CALL site — check it calls system-style args.

## Falsifier

Falsifier — none of the three is writable/reachable/firable: no %n redirect exists.
