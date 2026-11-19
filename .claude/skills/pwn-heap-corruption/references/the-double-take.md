# The double-alloc — same slot twice


Two add() calls returning the same address while both "live" — either a
dup (double-free'd bin) or a bookkeeping bug (slot array reuse).

## Verify

- add(); add() — if the second returns the first's address while the
  first is still marked live: a double-alloc.
- Write via slot A, read via slot B — the marker round-trip proves it.

## Falsifier

The service's slot tracking prevents it: overlap must come from the
bin-level techniques.
