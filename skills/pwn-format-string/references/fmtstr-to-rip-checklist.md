# Fmtstr to RIP — redirecting execution — checklist

The write primitive's goal is execution: overwrite a return address, a GOT entry, or a hook — the next return/call/malloc goes to your chain.

## Checklist

- [ ] Choose the redirect target: GOT entry (called next), ret-addr (return), __free_hook (next free).
- [ ] Write the chain's first address there via %n.
- [ ] The next call/return/alloc triggers the redirect.
- [ ] The redirect lands on a gadget or a useful function.

## Abort conditions

- The redirect target's CALL args come from the call site, not your fmtstr — check what's passed.
- A ret-addr redirect continues a ROP chain; a GOT redirect makes a call.

## Falsifier

Falsifier — no writable redirect target is reachable by the write primitive, or the redirect's arg state is wrong: no execution redirect.
