# Fmtstr to RIP — redirecting execution

The write primitive's goal is execution: overwrite a return address, a GOT entry, or a hook — the next return/call/malloc goes to your chain.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| a write primitive + a redirectable target | execution | the write |
| GOT / ret-addr / hook reachable | the redirect | choose it |
| the chain's first stage | a function or gadget | the target |

## Steps

1. Choose the redirect target: GOT entry (called next), ret-addr (return), __free_hook (next free).
2. Write the chain's first address there via %n.
3. The next call/return/alloc triggers the redirect.
4. The redirect lands on a gadget or a useful function.

## Falsifier

Falsifier — no writable redirect target is reachable by the write primitive, or the redirect's arg state is wrong: no execution redirect.

## Traps

- The redirect target's CALL args come from the call site, not your fmtstr — check what's passed.
- A ret-addr redirect continues a ROP chain; a GOT redirect makes a call.

## Cross-references

`got-overwrite-fmt.md` · `ret-addr-overwrite.md`
