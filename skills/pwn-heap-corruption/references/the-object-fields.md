# Object field analysis — what each byte means


When two objects overlap, WHICH fields alias decides the primitive:
offset 0x00 of object A might hit offset 0x10 of object B — map it.

## Steps

1. Note each object's field layout (source if present, else r2 -d
   inspection of a live object).
2. Compute the alias: A.base + k = B.field(j).
3. Choose the write that lands on the field you need.

## Common wins

- Aliasing a length field → expand a later write.
- Aliasing a pointer field → redirect reads/writes/calls.
- Aliasing a flag/state byte → skip a check.

## Falsifier

No field alignment produces a useful alias: the overlap is real but
sterile — overlap a different pair.
