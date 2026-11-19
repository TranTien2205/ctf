# The index array — where the pointers live — checklist

Companion to `index-array-bug.md`.

## Checklist

- [ ] Index bounds on every op — a negative or >=max index is an OOB read/
- [ ] Does delete clear ptr[i]? If not — UAF.
- [ ] Does add reuse a slot still marked live? Uninit slot use.
- [ ] The array's own address (non-PIE .bss) — a fixed write target.
