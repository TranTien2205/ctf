# The common failure — skipping the profile

The single most common memory-analysis failure: running pslist on
an unconfirmed profile and trusting the plausible-looking garbage
it prints. windows.info/banners is not optional — it validates the
whole session.

## The other frequent errors

- Dumping before naming a suspect — expensive and directionless.
- Treating a svchost as normal without checking its parent/path.
- Reading a pslist row as proof — it is a lead until the memory
  dump or a second plugin confirms.
- Forgetting UTF-16 — half the Windows strings are wide.
- Stopping at pslist — the flag is almost never in the list
  itself; it is in a dumped region, a cmdline, a file, or a key.

Each is a lead-vs-proof confusion — the evidence standard catches
them.

## The recovery

If a session has produced nothing but a pslist: go back to the
profile step, then name a suspect from the tail, then dump its
memory and hunt the token — the list itself was never the answer.
