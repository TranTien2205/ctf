# Field notes — what to record during a heap run


Record per run, so the kill-map survives:

- the glibc version and how it was determined
- the menu ops and their allocator mapping
- the bug's primitive (UAF/dup/overflow/oob)
- the leaks obtained (which source, which range)
- the technique attempted and the check that caught it (the abort
  message verbatim)
- the alloc/free sequence that worked
- the write target and its firing condition

A failed run with these notes is a reusable negative; a failed run
without them is lost work.
