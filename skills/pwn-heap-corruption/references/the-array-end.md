# Past the pointer array — the OOB read/write


When the slot index is unchecked, reads/writes past the pointer array
reach adjacent globals — the array OOB is its own primitive family.

## Steps

1. add/show/edit/delete accept index i — test i = -1, i = MAX+1.
2. OOB read: show(-1) reads the qword before the array — a pointer
   leak if a pointer lives there.
3. OOB write: edit(-1) writes it — a fixed-target write.
4. OOB free: delete(-1) frees an arbitrary pointer — fake-chunk fuel.

## Falsifier

Every index validated: the array is sealed — attack object internals.
