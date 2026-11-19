# Two frees, one chunk — the dup's anatomy


The double-free's mechanics: the bin holds the chunk twice; the alloc
walk consumes it twice — the second return is the overlap.

## The walk

    free(A): bin = A
    free(A): bin = A → A      # the dup
    alloc(): returns A; bin = A
    alloc(): returns A AGAIN  # A is live twice

## Falsifier

The second free is caught (key check or top check): no dup.
