# Restarting — ret to main for stage 2


After a leak, ret into main/the vuln function restarts the program —
the second pass delivers the real chain with known addresses.

## The shape

    <stage1: the leak chain>
    [main's entry or the read function]

## The state

Restarted state is fresh (new stack, same code+libc) — the leaked
addresses still apply (same mappings).

## Falsifier

No re-entry path (one-shot run): single-stage only.
