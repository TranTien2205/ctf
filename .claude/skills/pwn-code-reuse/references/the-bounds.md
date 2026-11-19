# The bounds — the chain's length limit


The chain's length is bounded by the read's limit — a chain longer
than the buffer truncates; the truncation's effect: the ending never
reaches.

## The measure

    chain_len = sum(qwords) ; bound = the read's limit

## Falsifier

The chain exceeds the bound: compress or stage it.
