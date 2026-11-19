# Past the pointer array — the OOB read/write — checklist

Companion to `the-array-end.md`.

## Checklist

- [ ] 1. add/show/edit/delete accept index i — test i = -1, i = MAX+1.
- [ ] 2. OOB read: show(-1) reads the qword before the array — a pointer
- [ ] 3. OOB write: edit(-1) writes it — a fixed-target write.
- [ ] 4. OOB free: delete(-1) frees an arbitrary pointer — fake-chunk fuel.
