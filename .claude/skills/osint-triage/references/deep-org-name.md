# Pivot depth: org-name

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

The `org-name` pivot's yield ranking across source
families, the format checks that validate it before
searching (a malformed pivot never returns), and the
transformations that turn it into the next pivot type.

## Transforms

Which derived pivots this type produces (handle->email
candidates, photo->hash, domain->IP) and which it cannot.
