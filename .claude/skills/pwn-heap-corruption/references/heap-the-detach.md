# Detached chunks — the inaccessible free


A chunk freed and consumed (sorted into a bin you can't reach, or
coalesced away): it's gone from your reach — the corruption window is
the time between free and consumption.

## The timing

- unsorted → sorted on the next malloc sweep.
- fastbin → consolidated on a large request.
- tcache → stays (no consolidation) — the stable window.

## Falsifier

The chunk is consumed before your corruption lands: the window closed.
