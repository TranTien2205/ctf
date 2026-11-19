# The final walk — the chain executed — checklist

Companion to `the-final-walk.md`.

## Checklist

- [ ] after pop rdi: rdi=binsh
- [ ] after ret: rsp+8 (aligned)
- [ ] at system: rdi=binsh, rsp aligned → the call is valid
- [ ] system's return → exit
