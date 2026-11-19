# The write-target table — GOT vs ret-addr vs hook

Three redirectable targets for a %n write: a GOT entry (call-time redirect), a saved return address (return-time), a malloc/free hook (alloc-time). Choose by what's reachable and what fires.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| partial RELRO + an import called next | GOT | the call |
| a known stack ret-addr | return | the ret |
| glibc ≤2.34 + a free after | free_hook | the alloc |
| the target's call-arg is right | the redirect calls it | arg check |

## Steps

1. GOT: partial RELRO, the import called next with the right arg.
2. Ret-addr: the stack address must be leaked/known; fires on return.
3. Hook: glibc ≤2.34; fires on the next malloc/free with the hooked arg.
4. Choose by which fires with a useful argument state.

## Falsifier

Falsifier — none of the three is writable/reachable/firable: no %n redirect exists.

## Traps

- GOT is the usual target (partial RELRO); hook for old glibc; ret-addr when stack addr is known.
- The redirect's arg comes from the CALL site — check it calls system-style args.

## Cross-references

`got-overwrite-fmt.md` · `ret-addr-overwrite.md` · `hooks-overwrite.md`
