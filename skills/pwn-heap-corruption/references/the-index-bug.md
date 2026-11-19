# The index-as-pointer bug — confusion


Some services index objects by a field INSIDE the object — corrupting
that field via overlap retargets the slot lookup.

## Steps

1. Object A holds an index/id field the lookup uses.
2. Overlap corrupts the index field.
3. The next lookup on A reads a different slot's pointer — confusion
   without touching the array.

## Falsifier

Lookups are array-index only: no field-driven indirection exists.
