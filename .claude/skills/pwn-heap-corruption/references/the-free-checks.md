# free() checks — the gates on deallocation


Every free() runs a gauntlet; the corruption must satisfy each check on
its path.

## The gates (in order)

1. Pointer alignment — chunk boundary (0x10 x64).
2. Size sanity — >= MINSIZE, sane upper bound.
3. Next-size sanity — the following chunk's size must be valid.
4. tcache key check (2.29+) — the double-free detector.
5. fastbin top check — top != victim.
6. Consolidation window — the merge's own checks.

## Reading aborts

Each abort names its check — the message IS the diagnosis.

## Falsifier

The corruption can't satisfy a gate on the only available path: that
route is closed; the check is the boundary, not the technique's skill.
