# Mapping the allocation lifecycle


Before any technique: which calls allocate, which free, what sizes,
what order, which objects carry pointers — the map the exploit is built
on.

## The inventory

- Menu ops → each maps to alloc/free/write/read — list them.
- Size of each object type — and which bin the size hits.
- Does the program keep pointers? Where (global array, struct fields)?
- Which objects carry pointers (name/desc/func fields) — the overlap
  targets.
- Which frees are reachable — and can ordering be influenced?

## Output

A table: op → alloc(size)/free(ptr) — the basis for the grooming plan.

## Falsifier

The program's interface can't express the needed sequence (fixed ops,
no reuse): the lifecycle doesn't support grooming — pick techniques
that work with the actual ops.
