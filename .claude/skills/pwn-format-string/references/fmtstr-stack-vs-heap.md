# Stack vs heap fmt buffer — where the input sits


The input buffer's location decides whether %N$p sees your bytes:
stack buffer — an arg; heap buffer — not an arg.

## Steps

1. Stack buffer: your bytes appear in the dump (the marker test).
2. Heap buffer: not an arg — %N$p can't reach your input.
3. The primitive still reads/writes args — just not via planted input.
4. Plant via an existing arg or a prior write.

## The test

Send marker bytes; if 0x41414141 shows in the dump: stack. If not:
heap or a different arg path.

## Falsifier

The marker never lands in any arg position: the input isn't
arg-reachable — reads only.
