# Two-stage — leak then write

Most format-string exploits are two-stage: the read leaks the values,
the write uses them.

1. Stage 1: %p run or %s read → canary, base, the target's address.
2. Stage 2: %n write → GOT/ret-addr/hook overwritten with the chain.

A looping/forking service re-triggers cleanly; a one-shot must compose
leak+write in one call.
