# The unsorted sort pass — where chunks get classified


The first _int_malloc unsorted sweep sorts leftover chunks into
small/large bins — a write-and-rearrange window.

## The pass

Each unsorted chunk is examined: exact-size match returns it; else
it's inserted into small or large bins (the unlink/insert writes run).

## Exploitation

- The insertion writes run during a normal malloc — corrupting a
  victim's links fires the write on the next alloc.
- The sort pass is where forged unsorted links get consumed.

## Falsifier

No malloc triggers the sweep (all requests fill from tcache/fastbin):
the pass never runs — force it with a bigger request.
