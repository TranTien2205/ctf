# Many-chunk overflows — the wide corruption


A long overflow forging several chunks' headers: a batch-corruption —
fewer ops, more forgery constraints.

## The setup

Every forged header must parse — size fields and flags consistent with
the NEXT forged header — a chain of fakes.

## Falsifier

The chain's internal consistency can't be satisfied: reduce to single-
chunk forgery.
