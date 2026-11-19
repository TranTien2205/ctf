# House of lore — smallbin recursive insert


Corrupt a smallbin victim's bk so a malloc's `last(bin)` walk follows
your chain: insert fake chunks into the smallbin, then harvest them.

## Steps

1. Victim V in smallbin. Forge fake F with F->fd = V and V->bk = F.
2. malloc of the smallbin size: the walk takes V, then F next.
3. Next malloc returns F — controlled memory.

## The chain

    fake->fd must point back into the bin (V) — the walk follows bk.

## Falsifier

The bin's first-entry check or the walk's consistency rejects the fake
link: lore needs both directions consistent.
