# Mapping the allocation lifecycle — checklist

Companion to `the-alloc-lifecycle.md`.

## Checklist

- [ ] Menu ops → each maps to alloc/free/write/read — list them.
- [ ] Size of each object type — and which bin the size hits.
- [ ] Does the program keep pointers? Where (global array, struct fields)?
- [ ] Which objects carry pointers (name/desc/func fields) — the overlap
- [ ] Which frees are reachable — and can ordering be influenced?
