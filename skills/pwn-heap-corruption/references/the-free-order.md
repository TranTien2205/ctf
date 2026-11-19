# The free order — sequencing the corruption


The order of frees decides the bin state: which chunk is tcache-top,
which is fastbin-top, which hits unsorted — the exploit's timing.

## The discipline

- Drain tcache (7 frees of size S) to route later frees elsewhere.
- A-B-A ordering defeats fastbin's top check.
- Free the victim LAST if you want it at the bin's head.
- Re-free after key-clearing for 2.29+ double-free.

## The plan

Script the sequence before running: alloc map → free order → expected
bin state → the alloc that harvests. Heap bugs are won on paper first.

## Falsifier

The program's free calls aren't under your ordering control (one fixed
free path): the sequence is fixed — design around the actual order.
