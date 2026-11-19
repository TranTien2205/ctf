# Overflow spanning several chunks


A large overflow crossing several chunk boundaries corrupts multiple
chunks' metadata at once — compound the forgery.

## Steps

1. Overflow past chunk A's data → B's header → C's header.
2. Forge B's size/flags AND C's — self-consistent fake chain.
3. A free/consolidate consumes the forged run — big overlap.

## Advantage

One write can set up a multi-chunk fake structure — fewer ops than
piecewise corruption.

## Falsifier

The write length caps below the next chunk's header: single-chunk
corruption only.
