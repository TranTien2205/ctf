# The index array — where the pointers live


Menu services store object pointers in a global array: ptr[i]. The
array itself is an attack surface — OOB indexes, uncleared entries,
double-slot use.

## The checks

- Index bounds on every op — a negative or >=max index is an OOB read/
  write/free primitive all by itself.
- Does delete clear ptr[i]? If not — UAF.
- Does add reuse a slot still marked live? Uninit slot use.
- The array's own address (non-PIE .bss) — a fixed write target.

## Falsifier

Every op bounds-checks and delete clears: the array is clean — attack
the objects, not the table.
