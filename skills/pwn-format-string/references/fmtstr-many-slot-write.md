# Writing several slots — the multi-target payload


One call can write to several addresses: each %N$hn consumes its own arg
position — a GOT entry AND a hook AND a ret-addr in one payload.

## Steps

1. Plant all target pointers at distinct arg positions.
2. %Nc %N$hn %Mc %O$hn ... — each write reads its own arg.
3. The count is shared — sequence the values.
4. Order matters: writes that fire mid-call (none do — all fire after
   printf returns) — safe to batch.

## Falsifier

The arg positions for all needed pointers can't be planted: reduce to
the essential write.
