# Fmtstr + ROP — the write that feeds the chain


The %n write lands the chain's first stage: overwrite the saved return
or a GOT entry with the ROP chain's first gadget — the fmtstr is the
entry, the ROP is the chain.

## The handoff

- The write lands a gadget's address → the chain's start.
- The ret-addr or GOT points to the chain → the redirect.

## Steps

1. Write the chain's first gadget address via %n.
2. The return/call redirects to it — the ROP chain runs.
3. Compose: leak (if needed) → %n write → chain executes.

## Falsifier

The write can't reach a redirectable slot, or the chain's first stage
isn't reachable: the composition fails.
