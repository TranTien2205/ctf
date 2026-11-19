# The heap checklist — the run in order


- [ ] glibc version named — the technique space is versioned
- [ ] bug primitive named — UAF/dup/overflow/oob/uninit
- [ ] alloc/free ops mapped — sizes, ordering, slots
- [ ] tcache routing — which sizes hit which bins
- [ ] libc leaked — unsorted fd/bk
- [ ] heap leaked — safe-linking pos (2.32+)
- [ ] stack leaked — environ or saved regs (if needed)
- [ ] technique chosen — matches version + primitive
- [ ] corruption scripted — not interactive
- [ ] overlap/write verified — marker or read-back
- [ ] redirect target — fires on a reachable event
- [ ] flag through hooks.py pre-flag
