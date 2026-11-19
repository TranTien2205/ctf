# Object field analysis — what each byte means — checklist

Companion to `the-object-fields.md`.

## Checklist

- [ ] 1. Note each object's field layout (source if present, else r2 -d
- [ ] 2. Compute the alias: A.base + k = B.field(j).
- [ ] 3. Choose the write that lands on the field you need.
- [ ] Aliasing a length field → expand a later write.
- [ ] Aliasing a pointer field → redirect reads/writes/calls.
- [ ] Aliasing a flag/state byte → skip a check.
