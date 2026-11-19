# cfree and friends — the alias frees


cfree, delete[], operator delete — the alias free paths all funnel to
the same _int_free; the checks are the same.

## Note

The bug class is identical regardless of which free symbol is used —
map by what reaches _int_free.

## Falsifier

None — naming note.
