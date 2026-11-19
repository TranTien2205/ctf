# The fmtstr checklist — the run in order


- [ ] Triage: pwn_triage — RELRO/PIE/canary noted
- [ ] Primitive: %p reflects a pointer — confirmed
- [ ] Offset: marker found — N named
- [ ] Leak: dump values classified — binary/libc/stack named
- [ ] Target: write slot chosen (GOT/ret/hook) — RELRO checked
- [ ] Plant: pointer at arg position — aligned
- [ ] Write: count math verified — the ledger
- [ ] Read-back: target value confirmed
- [ ] Fire: redirect triggers — observable result
- [ ] Flag: through hooks.py pre-flag
