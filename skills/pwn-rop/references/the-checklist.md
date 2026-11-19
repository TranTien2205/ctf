# The ROP checklist — the run in order


- [ ] IP control proven; the offset measured
- [ ] Protections read off the triage
- [ ] Leak needed? obtained? verified pointer-range?
- [ ] libc version identified (if libc used)
- [ ] Ending chosen; gadgets real (scanned, not remembered)
- [ ] /bin/sh sourced (found/planted/libc)
- [ ] Chain packed; the alignment ret placed
- [ ] Bad bytes checked against the transport
- [ ] Chain length within the read's bound
- [ ] Stage-verified under r2 -d
- [ ] The observable fired; the flag through the hook
