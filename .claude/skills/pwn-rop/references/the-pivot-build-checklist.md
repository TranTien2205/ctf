# The pivot — moving the stack — checklist

Companion to `the-pivot-build.md`.

## Checklist

- [ ] `pop rsp; ret` — rsp = the next qword.
- [ ] `leave; ret` — rsp = rbp; then a ret pops from there (set rbp
- [ ] `xchg rsp, rax; ret` — if rax holds the region.
- [ ] `add rsp, N; ret` — a partial skip.
